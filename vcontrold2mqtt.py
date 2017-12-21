#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


__app__ = "vcontrold2mqtt Adapter"
__VERSION__ = "0.1"
__DATE__ = "23.07.2017"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2017 Markus Schiesser"
__license__ = 'GPL v3'


import sys
import time
import json
import paho.mqtt.client as mqtt
from configobj import ConfigObj
from library.logger import logger
from library.vcontrold import vcontrold


class manager(object):

    def __init__(self,cfg_file='vcontrold2mqtt.cfg'):

        self._cfg_file = cfg_file

        self._cfg_broker = None
        self._cfg_log = None
        self._cfg_vclient = None
        self._cfg_commands = None

        self._mqttc = None
        self._vclient = None

        self._state = 'NOTCONNECTED'

        self._result ={}

    def read_config(self):
      #  print(self._cfg_file)
        _cfg = ConfigObj(self._cfg_file)

        self._cfg_broker = _cfg.get('BROKER',None)
        self._cfg_log = _cfg.get('LOGGING',None)
        self._cfg_vcontrold = _cfg.get('VCONTROLD',None)
        self._cfg_commands = _cfg.get('COMMANDS',None)
       # print(self._cfg_commands)
        return True

    def start_logger(self):
        self._log = logger('VCONTROLD2MQTT')
        self._log.handle(self._cfg_log.get('LOGMODE'),self._cfg_log)
        self._log.level(self._cfg_log.get('LOGLEVEL','DEBUG'))
        return True

    def read_vcontrold(self):
        print('read')
        self._vcontrold = vcontrold(self._cfg_vcontrold, self._log)
        self._vcontrold.connect()

        for item in self._cfg_commands.get('COMMANDLIST'):
            value = self._vcontrold._read(item)

            self._result[item]=str(value)
            print('TEST', item,value)
            self._log.debug('Read from Heating: %s , %s'% (item,str(value)))

            #self.mqttPublish(item,str(value))

    def mqttPublish(self):
        self._host = str(self._cfg_broker.get('HOST', 'localhost'))
        self._port = int(self._cfg_broker.get('PORT', 1883))
        self._publish = str(self._cfg_broker.get('PUBLISH', '/PUBLISH'))
        self._mqttc = mqtt.Client()

        self._mqttc.connect(self._host,self._port,60)
        for key,value in self._result.items():
            _topic = str(self._publish + '/' + key)

    #    print(_topic)
            print('Publish:', _topic, value)
            self._log.debug('Publish: %s , %s'% ( _topic, str(value)))
            self._mqttc.publish(_topic, value)
        # print('cc',channel,msg)
        self._mqttc.loop(2)
        self._mqttc.disconnect()
        return True

    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        self.read_config()
     #  print('ooo')
        self.start_logger()
      #  print('loger')
        # Log information
        msg = 'Start ' + __app__ +' ' +  __VERSION__ + ' ' +  __DATE__
        self._log.info(msg)

        self.read_vcontrold()
        self.mqttPublish()




if __name__ == "__main__":

    print ('main')
    if len(sys.argv) == 2:
        configfile = sys.argv[1]
    else:
        configfile = '/opt/vissmann2mqtt/vcontrold2mqtt.cfg'
    #    configfile = 'C:/Users/tgdscm41/PycharmProjects/Raspberry/vcontrold2mqtt/vcontrold2mqtt.cfg'
        #configfile =  '/home/pi/m2m/S02mqtt.cfg'

  #  print('Configfile',configfile)
    mgr_handle = manager(configfile)
    mgr_handle.run()
