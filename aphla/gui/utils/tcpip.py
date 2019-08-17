from __future__ import print_function, division, absolute_import

import sys, os
import ntpath, posixpath
from socket import (socket, AF_INET, SOCK_STREAM, gethostname,
                    SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR, timeout)
TimeoutError = timeout
import traceback
from random import randint
from subprocess import Popen, PIPE
from urllib2 import urlopen, ProxyHandler
from shutil import copy, move
import logging
from time import time

BLOCK_SIZE = 2048 # [bytes]

SERVER_NAME = 'lsasd2.ls.bnl.gov'

help_info = '''
'''

SERVER_PORT_NUMBER_FOLDERPATH = '/home/yhidaka/public_html'
SERVER_PORT_NUMBER_URL_PATH = 'http://lsasd2.ls.bnl.gov/~yhidaka' # Can omit "http://" if you use "wget" instead of "urlopen"
SERVER_PORT_NUMBER_FILENAME = 'server_port_number.txt'

########################################################################
class Client(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, server_name=SERVER_NAME,
                 server_port_number_filename=SERVER_PORT_NUMBER_FILENAME,
                 server_port_number_url_path=SERVER_PORT_NUMBER_URL_PATH,
                 logfilepath='tcpip_client.log'):
        """Constructor"""

        logging.basicConfig(filename=logfilepath,level=logging.DEBUG,
                            format='%(asctime)s:%(levelname)s:%(message)s')

        self.sock = self.getNewSocket()

        self.server_name = server_name
        self.server_port_number_filepath = posixpath.join(
            server_port_number_url_path, server_port_number_filename)

        self.server_port_number = None
        self.server_address = None

    #----------------------------------------------------------------------
    def getNewSocket(self):
        """"""

        return socket(AF_INET, SOCK_STREAM)

    #----------------------------------------------------------------------
    def closeSocket(self):
        """"""

        #self.sock.shutdown()
        self.sock.close()

    #----------------------------------------------------------------------
    def updateServerPortNumber(self, method='urlopen', disableProxy=True):
        """"""

        if os.name == 'nt':
            method = 'urlopen'

        if method == 'urlopen':
            if disableProxy:
                ProxyHandler({}) # Disabling proxy
            response = urlopen(self.server_port_number_filepath)
            server_port_number_str = response.read()
        elif method == 'wget':
            popen_arg_list = ['wget','-O-','-q',self.server_port_number_filepath]
            '''
            The -O... option means "write to the specified file",
            where - is standard output; the -q option means "quiet", and
            disables lots of logging that would otherwise go to standard error.
            '''
            if disableProxy:
                popen_arg_list.insert(1, '--no-proxy')
            p = Popen(popen_arg_list, stdout=PIPE, stderr=PIPE)
            server_port_number_str, error = p.communicate()
            if error:
                print('"wget" failed while trying to obtain server port number:')
                print(error)
                raise RuntimeError()
        else:
            raise ValueError('Unexpected "method" argument specified: '+method)

        try:
            server_port_number = int(server_port_number_str)
        except:
            print(('Invalid literal for int() with base 10:',
                   server_port_number_str.__repr__()))
            raise RuntimeError()

        self.server_port_number = server_port_number

    #----------------------------------------------------------------------
    def connectToServer(self, portFindMethod='urlopen', portFindProxyDiable=True,
                        timeout=3600., debug=False):
        """"""

        self.closeSocket()
        self.sock = self.getNewSocket()

        if self.server_address is not None:
            try:
                if debug:
                    print('connecting to {0} port {1}'.format(*self.server_address))
                self.sock.connect(self.server_address)
                return
            except:
                traceback.print_exc()
                print(('Connecting without server port number refresh failed. ',
                       'Will try connecting after refreshing server port number.'))

        self.updateServerPortNumber(
            method=portFindMethod, disableProxy=portFindProxyDiable)

        self.server_address = (self.server_name, self.server_port_number)
        if debug:
            print(('Server Addres:', self.server_address))

        try:
            if debug:
                print('connecting to {0} port {1}'.format(*self.server_address))
            self.sock.connect(self.server_address)
        except:
            traceback.print_exc()
            print('Failed to connect even after server port number refresh.')

        self.sock.settimeout(timeout)
        if debug:
            print(('Timeout set to', str(timeout), 'seconds.'))


    #----------------------------------------------------------------------
    def sendRequestHeader(self, header, timeout=3., debug=False):
        """
        """

        self.connectToServer(timeout=timeout)

        success = False
        try:
            self.sock.sendall(header)

            amount_received = 0
            amount_expected = len(header)
            while amount_received < amount_expected:
                data = self.sock.recv(BLOCK_SIZE)
                amount_received += len(data)
                if debug:
                    print('received "{0:s}"'.format(data))

            success = True
        except:
            traceback.print_exc()
            success = False
        finally:
            self.closeSocket()

        if not success:
            raise RuntimeError('Failed to send header to server.')


    #----------------------------------------------------------------------
    def _send_test_message(self):
        """"""

        try:
            self.sendRequestHeader('echo')
        except:
            print('ERROR: There appears to be a network problem.')
            print('Make sure that the server is running.')
            return

        self.connectToServer()

        test_message = 'This is the message. It will be repeated.'
        print('sending "{0:s}"'.format(test_message))

        try:

            self.sock.sendall(test_message)

            amount_received = 0
            amount_expected = len(test_message)
            while amount_received < amount_expected:
                data = self.sock.recv(BLOCK_SIZE)
                amount_received += len(data)
                print('received "{0:s}"'.format(data))
        except:
            traceback.print_exc()
        finally:
            self.closeSocket()

    #----------------------------------------------------------------------
    def sendFile(self, src_filepath, destination_folderpath='', timeout=600.,
                 debug=False):
        """"""

        try:
            self.sendRequestHeader('receiveFile')
        except:
            print('ERROR: There appears to be a network problem.')
            print('Make sure that the server is running.')
            return


        # Notify server which file is being sent
        src_absfilepath = os.path.abspath(src_filepath)
        src_folder_path, src_filename = os.path.split(src_absfilepath)
        #
        self.connectToServer(timeout=3.,debug=debug)
        self.sock.sendall(src_filename)
        self.closeSocket()

        # Notify the server where the sent file should be moved on the server.
        # If empty, the file should stay wherever the server is running.
        self.connectToServer(timeout=3.,debug=debug)
        self.sock.sendall(destination_folderpath)
        self.closeSocket()

        # Send the file
        self.connectToServer(timeout=timeout,debug=debug)
        try:
            f = open(src_absfilepath,'rb')
            print('Sending file...')

            while True:
                data = f.read(BLOCK_SIZE)
                if not data: f.close(); break
                self.sock.sendall(data)
                ## or
                #sent = self.sock.send(data)
                #assert sent == len(data)
            print('File sending finished successfully.')
        except:
            traceback.print_exc()
            print(('Error sending file to server:', src_absfilepath))
        #
        self.closeSocket()

    #----------------------------------------------------------------------
    def receiveFile(self, filename, src_folderpath='', timeout=600., debug=False):
        """"""

        try:
            self.sendRequestHeader('sendFile')
        except:
            print('ERROR: There appears to be a network problem.')
            print('Make sure that the server is running.')
            return


        # Notify server which file this client wants
        self.connectToServer(timeout=5.)
        self.sock.sendall(filename)
        self.closeSocket()

        # Specify the folder path on server where this file resides.
        # If empty, Server will assume you want the file within
        # its current working directory.
        self.connectToServer(timeout=5.)
        self.sock.sendall(src_folderpath)
        self.closeSocket()

        # Receive the file
        self.connectToServer(timeout=timeout)
        try:
            f = open(filename, 'wb')
            print('Receiving file...')

            while True:
                data = self.sock.recv(BLOCK_SIZE)
                if debug:
                    print('received "{0:s}"'.format(str(data)))
                if not data: f.close(); break
                f.write(data)
            print('File receiving finished successfully.')
        except:
            traceback.print_exc()
            print(('Error receiving file from server:', filename))
        #
        self.closeSocket()


########################################################################
class Server(object):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, server_port_number_filename=SERVER_PORT_NUMBER_FILENAME,
                 server_port_number_folderpath=SERVER_PORT_NUMBER_FOLDERPATH,
                 logfilepath='tcpip_server.log'):
        """Constructor"""

        logging.basicConfig(filename=logfilepath,level=logging.DEBUG,
                            format='%(asctime)s:%(levelname)s:%(message)s')

        self.sock = socket(AF_INET, SOCK_STREAM)
        self.is_bound = False

        self.name = gethostname()
        ''' This should return "lsasd2". The code will work if
        self.name is "lsasd2", "lsasd2.ls.bnl.gov", or
        lsasd2's IP address.
        '''

        self.server_port_number_filepath = os.path.join(
            server_port_number_folderpath, server_port_number_filename)

        self.port_number = None
        self.address = None

        self.task_list = []

    #----------------------------------------------------------------------
    def closeSocket(self):
        """"""

        #self.sock.shutdown(SHUT_RDWR)
        self.sock.close()

    #----------------------------------------------------------------------
    def openPort(self, nMaxTrials=10, debug=False):
        """"""

        if self.is_bound:
            print('Socket has already been bound.')
            return

        for i in range(nMaxTrials):
            self.port_number = randint(int(1e4),int(6e4))
            self.address = (self.name, self.port_number)
            print('starting up on {0} port {1}'.format(*self.address))
            try:
                self.sock.bind(self.address)
                break
            except:
                if debug:
                    traceback.print_exc()

                if i == nMaxTrials-1:
                    print('Maximum number of trials for finding an available port has failed.')
                    sys.exit()

        try:
            with open(self.server_port_number_filepath,'w') as f:
                f.write(str(self.port_number))
        except:
            raise IOError('Failed to write port number ('+ str(self.port_number) +
                          ')opened by server.')

        self.is_bound = True

    #----------------------------------------------------------------------
    def receiveString(self, debug=False):
        """"""

        connection, client_address = self.sock.accept()

        string = ''

        try:
            while True:
                data = connection.recv(BLOCK_SIZE)
                if debug:
                    print('received "{0:s}"'.format(data))
                if not data: break
                string += data
        except:
            traceback.print_exc()
            raise RuntimeError()

        print('receiveString finished successfully. Closing client connection.')
        connection.close()

        return string

    #----------------------------------------------------------------------
    def echo(self, connection=None, client_address='', debug=False):
        """
        The only difference from receiveString() is that this will return
        the received string back to Client. This is useful to know if the
        connection Client thought it made successfully is actually active
        or not, by confirming what has been received by Server.
        """

        if connection is None:
            connection, client_address = self.sock.accept()

        string = ''

        try:
            while True:
                data = connection.recv(BLOCK_SIZE)
                if debug:
                    print('received "{0:s}"'.format(data))
                if data:
                    string += data
                    connection.sendall(data)
                else:
                    break
        except:
            traceback.print_exc()
            raise RuntimeError()

        if debug:
            print('Echo finished successfully. Closing client connection.')
        connection.close()

        return string

    #----------------------------------------------------------------------
    def receiveFile(self, debug=False):
        """"""

        filename = self.receiveString()
        destination_folderpath = self.receiveString()

        connection, client_address = self.sock.accept()
        try:
            f = open(filename, 'wb')
            print('Receiving file...')

            while True:
                data = connection.recv(BLOCK_SIZE)
                if debug:
                    print('received "{0:s}"'.format(str(data)))
                if not data: f.close(); break
                f.write(data)

            print('File receiving finished successfully.')
        except:
            traceback.print_exc()
            raise RuntimeError()

        if destination_folderpath != '':
            destination_folderpath = os.path.normpath(destination_folderpath)
            move(filename, os.path.join(destination_folderpath,filename))

        print('Closing client connection.')
        connection.close()

    #----------------------------------------------------------------------
    def sendFile(self, debug=False):
        """"""

        filename = self.receiveString()
        src_folderpath = self.receiveString()

        connection, client_address = self.sock.accept()
        try:
            if src_folderpath != '':
                filepath = os.path.join(src_folderpath,filename)
            else:
                filepath = os.path.abspath(filename)

            f = open(filepath, 'rb')
            print('Sending file...')

            while True:
                data = f.read(BLOCK_SIZE)
                if not data: f.close(); break
                connection.sendall(data)
            print('File sending finished successfully.')
        except:
            traceback.print_exc()
            raise RuntimeError()

        print('Closing client connection.')
        connection.close()


    #----------------------------------------------------------------------
    def startListening(self, nMaxQueuedConnections=0):
        """"""

        #self.closeSocket()
        self.openPort()

        self.sock.listen(nMaxQueuedConnections)

        timeout_list = [task.client_connection_timeout
                        for task in self.task_list]
        if timeout_list == []:
            self.sock.settimeout(None)
        else:
            self.sock.settimeout(min(timeout_list))

        for task in self.task_list:
            if callable(task.initialFunc):
                task.initialFunc()

        stop_requested = False
        show_wait_print = True
        while not stop_requested:

            if show_wait_print:
                print('waiting for a connection')

            try:
                connection, client_address = self.sock.accept()
            except TimeoutError:
                #print('timed out waiting for a connection')
                for task in self.task_list:
                    if task.pastScheduledTime() and \
                       callable(task.periodicFunc):
                        task.periodicFunc()
                show_wait_print = False
                continue
            except KeyboardInterrupt:
                print('Stop requested by user')
                stop_requested = True
                continue
            else:
                show_wait_print = True

            try:
                header = self.echo(connection, client_address)
                print('client header:', header)

                not_implemented_message = (
                    'You must implement a function called "'+
                    header+'" in Server class.')

                if hasattr(self, header):
                    request_func_obj = getattr(self, header)
                    if callable(request_func_obj):
                        # Run the specified function
                        request_func_obj()
                    else:
                        raise NotImplementedError(not_implemented_message)
                else:
                    raise NotImplementedError(not_implemented_message)
            except KeyboardInterrupt:
                print('Stop requested by user')
                stop_requested = True
                continue
            except:
                continue

        else:
            for task in self.task_list:
                if callable(task.finalFunc):
                    task.finalFunc()

########################################################################
class ServerTask():
    """"""

    #----------------------------------------------------------------------
    def __init__(self, min_interval, client_connection_timeout):
        """Constructor"""

        self.min_interval = min_interval
        '''
        A minimum periodic interval in seconds at which the task defined
        by this class must be performed on the server.
        '''

        self.client_connection_timeout = client_connection_timeout
        '''
        If the server does not receive any connection request from
        clients for this amount of time duration, then the server will
        check if the specified minimum interval time has elapsed. If yes,
        then the server will perform the specified task function
        "periodicFunc". If not, the server will start waiting for
        a connection request again.

        Therefore, this timeout must be carefully chosen. You want to set
        this timeout much smaller than min_interval if you want the tasks
        to be performed as accurate to the schedule as possible.

        If you set the timeout too long, and the server receives frequent
        connection requests, then this task may never be performed.

        On the other hand, if you set this timeout too small, the server
        will frequently check if the task should be performed.
        '''

        self.last_timestamp = time()

        self.initialFunc = None
        self.periodicFunc = None
        self.finalFunc = None

    #----------------------------------------------------------------------
    def pastScheduledTime(self):
        """"""

        current_timestamp = time()
        elapsed_time = current_timestamp - self.last_timestamp

        if elapsed_time >= self.min_interval:
            self.last_timestamp = current_timestamp
            return True
        else:
            return False
