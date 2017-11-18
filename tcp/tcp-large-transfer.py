# -*-  Mode: Python; -*-
# /*
#  * Copyright (c) 2017 NITK Surathkal
#  *
#  * This program is free software; you can redistribute it and/or modify
#  * it under the terms of the GNU General Public License version 2 as
#  * published by the Free Software Foundation;
#  *
#  * This program is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  * GNU General Public License for more details.
#  *
#  * You should have received a copy of the GNU General Public License
#  * along with this program; if not, write to the Free Software
#  * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#  *
#  * Ported to Python by:
#  * Adarsh Honawad <adarsh2397@gmail.com>
#  * Sagar Bharadwaj <sagarbharadwaj50@gmail.com>
#  * Samvid Dharanikota <samvid25@yahoo.com>		
#  */

# //
# // Network topology
# //
# //           10Mb/s, 10ms       10Mb/s, 10ms
# //       n0-----------------n1-----------------n2
# //
# //
# // - Tracing of queues and packet receptions to file 
# //   "tcp-large-transfer.tr"
# // - pcap traces also generated in the following files
# //   "tcp-large-transfer-$n-$i.pcap" where n and i represent node and interface
# // numbers respectively
# //  Usage (e.g.): ./waf --pyrun examples/tcp-large-transfer

import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point

# // The number of bytes to send in this simulation.
totalTxBytes = 2000000
currentTxBytes = 0
# // Perform series of 1040 byte writes (this is a multiple of 26 since
# // we want to detect data splicing in the output stream)
writeSize = 1040
data = [0]*writeSize

# // These are for starting the writing process, and handling the sending 
# // socket's notification upcalls (events).  These two together more or less
# // implement a sending "Application", although not a proper ns3.Application
# // subclass.

# // begin implementation of sending "Application"
def StartFlow(localSocket, servAddress, servPort):
	print "Starting flow at time", ns.core.Simulator.Now().GetSeconds()

	# // connect
	localSocket.Connect(ns.network.InetSocketAddress(servAddress, servPort));
	# // tell the tcp implementation to call WriteUntilBufferFull again
  	# // if we blocked and new tx buffer space becomes available
	localSocket.SetSendCallback(WriteUntilBufferFull)
	WriteUntilBufferFull(localSocket, localSocket.GetTxAvailable());

def WriteUntilBufferFull(localSocket, txSpace):
	global data
	global currentTxBytes
	global totalTxBytes
	while currentTxBytes < totalTxBytes and  localSocket.GetTxAvailable() > 0:
		left = totalTxBytes - currentTxBytes
		dataOffset = currentTxBytes % writeSize
		toWrite = writeSize - dataOffset
		toWrite = min(toWrite, left)
		toWrite = min(toWrite, localSocket.GetTxAvailable())
		amountSent = localSocket.Send(ns.network.Packet(data[dataOffset]), 0)

		if amountSent < 0:
			# // we will be called again when new tx space becomes available.
			return;

		currentTxBytes += amountSent
	
	localSocket.Close()

# // def CwndTracer(oldval, newval):
# // 	print "Moving cwnd from" + oldval + " to " + newval

def main(argv):
	cmd = ns.core.CommandLine()
	cmd.Parse(argv)

  	# // initialize the tx buffer.
	for i in range(writeSize):
		m = 97 + i%26
		data[i] = m

	# // Here, we will explicitly create three nodes.  The first container contains
	# // nodes 0 and 1 from the diagram above, and the second one contains nodes
	# // 1 and 2.  This reflects the channel connectivity, and will be used to
	# // install the network interfaces and connect them with a channel.
	n0n1 = ns.network.NodeContainer()
	n0n1.Create(2)

	n1n2 = ns.network.NodeContainer()
	n1n2.Add(n0n1.Get(1))
	n1n2.Create(1)

	# // We create the channels first without any IP addressing information
	# // First make and configure the helper, so that it will put the appropriate
	# // attributes on the network interfaces and channels we are about to install.
	p2p = ns.point_to_point.PointToPointHelper()
	p2p.SetDeviceAttribute ("DataRate", ns.network.DataRateValue (ns.network.DataRate (10000000)))
	p2p.SetChannelAttribute("Delay", ns.core.TimeValue(ns.core.MilliSeconds(10)))

	# // And then install devices and channels connecting our topology.
	dev0 = p2p.Install(n0n1)
	dev1 = p2p.Install(n1n2)

	# // Now add ip/tcp stack to all nodes.
	internet = ns.internet.InternetStackHelper()
	internet.InstallAll()

	# // Later, we add IP addresses.
	ipv4 = ns.internet.Ipv4AddressHelper()
	ipv4.SetBase(ns.network.Ipv4Address("10.1.3.0"),ns.network.Ipv4Mask("255.255.255.0"))
	ipv4.Assign(dev0)
	ipv4.SetBase(ns.network.Ipv4Address("10.1.2.0"),ns.network.Ipv4Mask("255.255.255.0"))
	ipInterfs = ipv4.Assign(dev1)

	# // and setup ip routing tables to get total ip-level connectivity.
	ns.internet.Ipv4GlobalRoutingHelper().PopulateRoutingTables()

	#####################################################################
	# Simulation 1
	#
	# Send 2000000 bytes over a connection to server port 50000 at time 0
	# Should observe SYN exchange, a lot of data segments and ACKS, and FIN 
	# exchange.  FIN exchange isn't quite compliant with TCP spec (see release
	# notes for more info)
	#
	#####################################################################
	servPort = 50000

	# // Create a packet sink to receive these packets on n2...
	sink = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory",ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), servPort))
	sinkApps = sink.Install(n1n2.Get(1))
	sinkApps.Start(ns.core.Seconds(0.0))
	sinkApps.Stop(ns.core.Seconds(3.0))

	# // Create a source to send packets from n0.  Instead of a full Application
	# // and the helper APIs you might see in other example files, this example
	# // will use sockets directly and register some socket callbacks as a sending
	# // "Application".

	# // Create and bind the socket...
	localSocket = ns.network.Socket.CreateSocket(n0n1.Get(0), ns.core.TypeId.LookupByName("ns3::TcpSocketFactory"))
	localSocket.Bind()

	# // Trace changes to the congestion window
	# // ns.core.Config.ConnectWithoutContext("/NodeList/0/$ns3::TcpL4Protocol/SocketList/0/CongestionWindow", ns.core.CallbackBase(CwndTracer))

	# // ...and schedule the sending "Application"; This is similar to what an 
	# // ns3::Application subclass would do internally.
	ns.core.Simulator.ScheduleNow(StartFlow,localSocket,ipInterfs.GetAddress(1),servPort)

	# // One can toggle the comment for the following line on or off to see the
	# // effects of finite send buffer modelling.  One can also change the size of
	# // said buffer.
	# // localSocket.SetAttribute("SndBufSize", ns.core.UintegerValue(4096))

	# //Ask for ASCII and pcap traces of network traffic
	ascii = ns.network.AsciiTraceHelper ()
	p2p.EnableAsciiAll (ascii.CreateFileStream ("tcp-large-transfer-py.tr"))
	p2p.EnablePcapAll ("tcp-large-transfer-py", True)

	# // Finally, set up the simulator to run.  The 1000 second hard limit is a
	# // failsafe in case some change above causes the simulation to never end
	ns.core.Simulator.Stop(ns.core.Seconds(1000))
	ns.core.Simulator.Run()
	ns.core.Simulator.Destroy()

if __name__ == '__main__':
    import sys
    main (sys.argv)


