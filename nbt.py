import os, gzip, array, struct
from contextlib import closing

try:
    import cStringIO as StringIO
except:
    import StringIO


Tag = None

class TagMeta(type):
    def __init__(cls, name, bases, attrs):
        if Tag is None:
            return
        Tag.types[cls.type] = cls


class Tag(object):
    __metaclass__ = TagMeta

    types = {}
    type = None
    fmt = ">b"
    dataType = str

    def __repr__(self):
        return "%s(%r): %r" % (self.__class__.__name__, self.name, self.value)

    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
    
    def load(self, nbt):
        self.value = self.dataType( nbt.unpack(self.fmt) )
    
    def save(self, nbt):
        nbt.pack(self.fmt, self.value)

class Long(Tag):
    type = 4;
    fmt = ">q";
    dataType = long

class Byte(Tag):
    type = 1;
    fmt = ">b";
    dataType = int
    
class Short(Tag):
    type = 2;
    fmt = ">h";
    dataType = int

class Int(Tag):
    type = 3;
    fmt = ">i";
    dataType = int

class Long(Tag):
    type = 4;
    fmt = ">q";
    dataType = long

class Float(Tag):
    type = 5;
    fmt = ">f";
    dataType = float

class Double(Tag):
    type = 6;
    fmt = ">d";
    dataType = float

class String(Tag):
    "String in UTF-8"

    type = 8
    fmt = ">h%ds"
    dataType = str

    def load(self, nbt):
        self.value = self.dataType( nbt.read_string() )

    def save(self, nbt):
        nbt.write_string(self.value)
    
    def __unicode__(self):
        return self.value

class List(Tag):
    type = 9

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.name)

    def __init__(self, name=None, content_type=None, value=None):
        super(List, self).__init__(name, value or [])
        self.content_type = content_type
    
    def load(self, nbt):
        self.content_type = nbt.read_byte()
        sz = nbt.read_int()
        for i in range(sz):
            tag = nbt.load_tag(self.content_type)
            self.value.append( tag )
    
    def save(self, nbt):
        values = filter(lambda x: x is not None, self.value)
        nbt.write_byte(self.content_type)
        nbt.write_int(len(values))
        print self
        for tag in values:
            if tag is not None:
                tag.save(nbt)
                print " ", tag
    
    "collection functions"
    def __getitem__(self, k):
        return self.value[k]
  
    def __iter__(self):
        return iter(self.value)
    
    def __contains__(self, k):
        return k in self.value

    def __len__(self):
        return len(self.value)
    
    def append(self, tag):
        if not isinstance(tag, Tag):
            raise TypeError("Appending object that is not a Tag: %r" % tag)
        tag.name = ""
        self.value.append(tag)

    def insert(self, pos, tag):
        if not isinstance(tag, Tag):
            raise TypeError("Inserting object that is not a Tag: %r" % tag)
        tag.name = ""
        self.value.insert(pos, tag)
    
    def pop(self, pos):
        return self.value.pop(pos)


class Tree(Tag):
    type = 10

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.name)

    def __init__(self, name=None, value=None):
        super(Tree, self).__init__(name, value or [])
    
    def load(self, nbt):
        while True:
            tag = nbt.load_tag(named=True)
            if tag is None:
                break
            self.value.append( tag )

    def save(self, nbt):
        for tag in self.value:
            if tag is None: continue
            nbt.write_byte(tag.type)
            nbt.write_string(tag.name)
            tag.save(nbt)
        nbt.write_byte(0)
    
    def __getitem__(self, k):
        for tag in self.value:
            if tag.name == k:
                return tag
        raise KeyError(k)
  
    def __iter__(self):
        return (tag.name for tag in self.value)

    def __contains__(self, k):
        for tag in self.value:
            if tag.name == k:
                return True
        return False

    def __len__(self):
        return len(self.value)

    def __setitem__(self, k, tag):
        if not isinstance(tag, Tag):
            raise TypeError("Setting object that is not a Tag: %r" % tag)
        for i, tag in enumerate(self.value):
            if tag.name == k:
                del self.value[i]
                self.value.insert(i, tag)
                return
        self.value.append(tag)
    
    def __delitem__(self, k):
        self.values.remove(k)
    
    def pop(self, k, default=None):
        for i, tag in enumerate(self.value):
            if tag.name == k:
                del self.value[i]
                return tag
        return default
    
    def add(self, tag):
        if not isinstance(tag, Tag):
            raise TypeError("Adding object that is not a Tag: %r" % tag)
        self.__setitem__(tag.name, tag)


class Nbt(object):    
    def __init__(self, filename=""):
        if filename:
            self.load(filename)

    def pop(self, count=1):
        return self.data.read(count)

    def unpack(self, format):
        try:
            count = struct.calcsize(format)
            data = self.pop(count)
            return struct.unpack_from(format, data)[0]
        except:
            print "Format:", format
            print "Data:", repr(data)
            raise

    def read_byte(self):
        return self.unpack(">b")

    def read_int(self):
        return self.unpack(">i")

    def read_string(self):
        sz = self.unpack(">h")
        if (sz == 0):
            return ""
        return self.unpack("%ds" % sz)

    def write_byte(self, val):
        self.pack(">b", val)
    
    def write_int(self, val):
        self.pack(">i", val)

    def write_string(self, string):
        fmt = "%ds" % len(string)
        self.pack(">h", len(string))
        self.pack(fmt, string)

    def pack(self, fmt, value):
        self.buffer.write( struct.pack(fmt, value) )

    def load_tag(self, typ=None, named=False):
        if typ is None:
            typ = self.read_byte()

        if typ == 0:
            return None
        
        cls = Tag.types.get(typ)
        if cls is None:
            raise RuntimeError("No class for type: %s" % typ)
        
        if named:
            try:
                name = self.read_string()
            except:
                print "Error on type:", typ
                raise
        else:
            name = None

        tag = cls(name)
        tag.load(self)
        return tag

    def load(self, filename):
        self.cursor = 0
        self.data = None
        self.root = None
        
        file = gzip.GzipFile(filename, mode="rb")
        try:
          data = file;
        except IOError:
          data = open(filename, "rb");
        
        self.data = data #array.array('b', data)

        self.root = self.load_tag(named=True)
        return self.root
    
    def save(self, filename, compresslevel=1):
        self.buffer = None

        if (self.root.name is None):
            self.root.name = ""
        
        if os.path.exists(filename):
            if (os.path.exists(filename + ".old")):
                os.unlink(filename + ".old")
            
            try:
                os.rename(filename, filename + ".old")
            except:
                pass
        
        try:
            self.buffer = gzip.open(filename, mode="wb", compresslevel=compresslevel)
            
            self.write_byte(self.root.type)
            self.write_string(self.root.name)
            self.root.save(self)
            
            self.buffer.close()
        except:
            self.buffer.close()
            if os.path.exists(filename):
                os.unlink(filename)
            if os.path.exists(filename + ".old"):
                os.rename(filename + ".old", filename)
            raise
            

def load(filename):
    return Nbt(filename).root

def save(root, filename):
    nbt = Nbt()
    nbt.root = root
    nbt.save(filename)

if(__name__=="__main__") :
    print "Starting..."
    nbt = load("level.dat")
    print "\nSaving..."
    nbt.save("level.dat.copy")
    print "Saved.\n"
    nbt = load("level.dat.copy")
    print "Done."
