# Instructions on how to use the package: https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html

# also needs to be tested!

try:
    import pysftp
except Exception as e:
    print("Some modules are missing {}".format(e))

class SFTP():
    
    def __init__(self, 
                 hostname:   str,
                 username:   str,
                 password:   str,
                 knownhosts: str=''):

        self.hostname  = hostname
        self.username  = username
        self._password = password
        
        if knownhosts != '':
            self._cnopts = pysftp.CnOpts(knownhosts=knownhosts)
            self._cnopts.hostkeys = None
        else:
            self._cnopts = pysftp.CnOpts()

        self._cnopts.log = True

        self.remotedir = str()
        self.localdir  = str()

        # self._checkConnection()  # still needs to be checkt if working!

    def _checkConnection(self):
        
        '''
        TO DO: Find a way to check if the connection is working 
        '''
        
        try:
            conn = pysftp.Connection(host     = self.hostname,
                                     username = self.username,
                                     password = self._password,
                                     cnopts   = self._cnopts)
            conn.close()
        except:
            raise ConnectionError("SFTP connection could not been initiated. Check connection initials!")

    def _connection(self):
        
        '''
        Opens SFTP-Connection with given initials and closes it automaticly after use (done by the with method of python).
        '''
        
        with pysftp.Connection(host=self.hostname, username=self.username,
                               password=self._password, cnopts=self._cnopts) as connection:

            yield connection

    def setTransferDirectories(self, remotedir: str, localdir: str):
        
        '''
        Sets the directory in the SFTP-server from or to which to copy files from, as well as the local target directory.

        *args:
            remotedir(str): Directory at the SFTP-server from or to which to copy files from
            localdir(str): Local directory to which the loaded files will be copied to or from
        '''
        
        self.remotedir = remotedir
        self.localdir  = localdir
    
    def downloadFiles(self, remotedir: str, localdir: str):
        
        '''
        pysftp.connection.get_r recursively copies files and directories from the remote to a local path. 
        With preserve_mtime the modification times on the local copy match those on the server.

        *args:
            remotedir(str): Directory at the SFTP-server from which to copy files from
            localdir(str): Local directory to which the loaded files will be copied to
        '''     
        
        self.setTransferDirectories(remotedir, localdir)

        with pysftp.Connection(
            host     = self.hostname,
            username = self.username,
            password = self._password,
            cnopts   = self._cnopts) as connection:

            if connection.exists(self.remotedir):
                connection.get_r(
                    remotedir = self.remotedir, 
                    localdir = self.localdir, 
                    preserve_mtime = True)

            else:
                raise "remotedir on SFTP-server dose not exist or leads to problems!"

    def uploadFiles(self, remotedir: str, localdir: str):
        
        '''
        pysftp.connection.get_r recursively copies files and directories from the localdir to the remotedir. 
        With preserve_mtime the modification times on the local copy match those on the server.
        A conformation about the correct file size after the transfer will be given.

        *args:
            remotedir(str): Directory at the SFTP-server to which to copy files from
            localdir(str): Local directory to which the loaded files will be copied from
        '''      
          
        self.setTransferDirectories(remotedir, localdir)

        with pysftp.Connection(
            host=self.hostname,
            username=self.username,
            password=self._password,
            cnopts=self._cnopts) as connection:

            if not connection.exists(self.remotedir):
                connection.mkdir(self.remotedir)
                
            connection.put_r(
                localpath = self.localdir, 
                remotepath = self.remotedir, 
                confirm = True, 
                preserve_mtime = True)