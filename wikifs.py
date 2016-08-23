import wikipedia as wiki
#import fakewiki as wiki
import llfuse

import os
import sys
import errno
import logging
import stat
from llfuse import FUSEError
import  os
from collections import defaultdict
from argparse import ArgumentParser
from time import time

try:
    import faulthandler
except ImportError:
    pass
else:
    faulthandler.enable()

log = logging.getLogger()




# class wikifs(LoggingMixIn, Operations):
#
#     page = None
#
#     def __init__(self, page_title = "New York"):
#         print "init"
#         self.page = wikipedia.page(page_title)
#
#     def getattr(self):
#         print "getattr"
#
#         return dict(st_mode=(S_IFREG | S_IROTH), st_nlink=1,
#                                 st_size=len(self.page.content.encode('utf-8')), st_ctime=time(), st_mtime=time(),
#                                 st_atime=time())
#
#     def open(self):
#         print "open"
#
#     def read(self):
#         print "read"
#         return self.page.content
#
#     def readdir(self):
#         print "readdir"
#
#         return ['.', '..'] + [name.encode('utf-8') for name in self.page.links]

#fuse = FUSE(wikifs(), argv[1], foreground=True, nothreads=True)

#obj = wikifs("New York")
#obj2 = obj.readdir()

#print obj2


class Operations(llfuse.Operations):

    def __init__(self, root_page):
        super(Operations, self).__init__()

        self.root_page = root_page
        print "root is ", self.root_page

        self.pages = {}
        self.nodes = {}
        self.fileHandlers = {}
        
        #we need to load the root
        
        
        self.pages[root_page] = wiki.page(root_page)
        node_id = hash(self.pages[root_page].title)
        
        self.nodes[node_id] = self.pages[root_page]
        
        #have a root page act as the root dir
        #self.nodes[1] = self.pages[root_page]
        
        log.debug("Fetched page: %s", self.pages[root_page])
        log.debug("Root page loaded")
        



    # def getattr(self, inode, ctx=None):
    #
    #     entry = llfuse.EntryAttributes()
    #     entry.st_ino = 0
    #     entry.generation = 0
    #     entry.entry_timeout = 300
    #     entry.attr_timeout = 300
    #     entry.st_mode = (stat.S_IFDIR | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
    #             stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
    #             stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
    #     entry.st_nlink = 1
    #     entry.st_uid = 1000
    #     entry.st_gid = 100
    #     entry.st_rdev = 0
    #     entry.st_size = 0
    #
    #     entry.st_blksize = 512
    #     entry.st_blocks = 1
    #     entry.st_atime_ns = int(time() * 1e9)
    #     entry.st_mtime_ns = int(time() * 1e9)
    #     entry.st_ctime_ns = int(time() * 1e9)
    #
    #     return entry
    #
    # def opendir(self, inode, ctx):
    #     return inode
    #
    # def readdir(self, inode, off):
    #     list = [1,2,3,4]
    #
    #     for item in list:
    #         yield item. self.getattr(item)

    def flush(self, node_no):
        print "flush ",node_no
    def release(self, node_no):
        print "release ",node_no

    def getattr(self, node_id):
        
        

        entry = llfuse.EntryAttributes()

        if node_id == llfuse.ROOT_INODE:
            print "ITS THE ROOT!! PANIC"
            log.debug("Looking at ROOT - ID:  %d",node_id)
            entry.st_mode = (stat.S_IFDIR | 0o755)
            entry.st_size = 0
        elif node_id in self.nodes:
            log.debug("Looking at %s - ID: %d ",self.nodes[node_id].title, node_id)
            entry.st_mode = (stat.S_IFDIR | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP |
                stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
            entry.st_size = 4096
            #entry.st_size = len(self.nodes[node_id].content.encode('utf-8'))

        entry.st_ino = node_id

        entry.entry_timeout = 300
        entry.attr_timeout = 300

        entry.st_nlink = 1
        entry.st_uid = 1000
        entry.st_gid = 100



        entry.st_atime_ns = int(time() * 1e9)
        entry.st_mtime_ns = int(time() * 1e9)
        entry.st_ctime_ns = int(time() * 1e9)

        return entry


    #TODO this currently works around the idea of file pointers, fix it
    def open(self, inode_no, flags):

        return inode_no


        #TODO this currently works around the idea of file pointers, fix it
    def opendir(self, inode_no):

        return inode_no

    def releasedir(self, fh):
        log.debug("Not implamented")

    def read(self, fh, offset, size):

        return self.nodes[fh].content.encode('utf-8')[offset:offset+size]

    def readdir(self, fh, offset):
        if fh == llfuse.ROOT_INODE:
            print "root is called", self.root_page
            if offset == 0:
                print "only one listing in root"
            
            ##ERROR HERE, cant call up self.root_page before its added
                attr = self.lookup( 0, self.root_page)

                yield  self.root_page, attr, offset+1
            
        else:
        #    yield  self.nodes[fh].link[fh], self.lookup(hash(self.pages[fh].title), self.nodes[fh].link[fh]), offset+1
            print "fh: " + str(fh) + " - offset: " + str(offset)
            print "ROOT IS" + str(llfuse.ROOT_INODE)
            print(self.nodes)
            print(self.pages)
        
            a= self.nodes[fh].links[offset]
            print("A: ",a)
            b = self.lookup(hash(self.nodes[fh].title), self.nodes[fh].links[offset])
            print("b: ",b)
            print(self.pages[a].title)
        
        
            yield  self.nodes[fh].links[offset].title, self.lookup(hash(self.nodes[fh].title), self.nodes[fh].links[offset].title), offset+1
        #yield 1, "root", offset+1
        
        

    def lookup(self, parent_inode, name, ctx=None):
        #if parent_inode != llfuse.ROOT_INODE or name != self.hello_name:
        #    raise llfuse.FUSEError(errno.ENOENT)

        #TODO erros occur here when a link in a page directs to a page with a different name e.g "New York" -> "City of New York"

        print "WE ARE HERE ",name," AND ",parent_inode
        if name not in self.pages:
            log.debug("Page not found, loading: %s", name)
            self.pages[name] = wiki.page(name)
            #Use the name it should have rather then the real name
            node_id = hash(name)
            #node_id = hash(self.pages[name].title)
            self.nodes[node_id] = self.pages[name]
        else:
            node_id = hash(name)
        log.debug("looked up page: %s", self.pages[name])
        log.debug("should have looked up: %s", name)
        return self.getattr(node_id)



def parse_args():
    '''Parse command line'''

    parser = ArgumentParser()

    parser.add_argument('mountpoint', type=str,
                        help='Where to mount the file system')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Enable debugging output')
    parser.add_argument('--debug-fuse', action='store_true', default=False,
                        help='Enable FUSE debugging output')
    parser.add_argument('--homepage', type=str,
                        help='The first page', default="York")

    return parser.parse_args()


def init_logging(debug=False):
    formatter = logging.Formatter('%(threadName)s -- [%(name)s] -- %(funcName)s -- %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    if debug:
        handler.setLevel(logging.DEBUG)
        root_logger.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

if __name__ == '__main__':

    options = parse_args()
    init_logging(options.debug)

    operations = Operations(options.homepage)

    default_options = ['big_writes', 'nonempty', 'fsname=tmpfs', 'debug',
                             'no_splice_read', 'splice_write', 'splice_move']

    llfuse.init(operations, options.mountpoint, default_options)

    try:
        llfuse.main(single=True)
    except:
        llfuse.close(unmount=True)
        raise

    llfuse.close()

