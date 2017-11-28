"""
 Network topology

       n0              n1
       |               |
       =================
              LAN

 - UDP flows from n0 to n1
"""

import ns3
import ns.core
import ns.network
import ns.csma
import ns.internet
import ns.applications
import sys

def ReceivePacket(socket):
	print "Received one packet!"
	packet=socket.Recv()

	tclassTag = ns3.socket.SocketIpv6TclassTag()
	if packet.RemovePacketTag(tclassTag) == True:
		print (" TCLASS = ", tclassTag.GetTclass ())

	hoplimitTag = ns3.socket.SocketIpv6HopLimitTag
	if packet.RemovePacketTag(hoplimitTag) == True:
		print (" HOPLIMIT = ", hoplimitTag.GetHopLimit ())
	
def SendPacket (args, socket, pktSize, pktCount, pktInterval):
  	
  	if pktCount > 0 :
		print "packet sent"     		
		p = ns.network.Packet(pktSize)
     		socket.Send (p)
    		ns.core.Simulator.Schedule (pktInterval, SendPacket,"args", socket, pktSize,pktCount - 1, pktInterval)
			
	else:
     		socket.Close ()
		

def main(argv):

	# Allow the user to override any of the defaults and the above Bind() at
	# run-time, via command-line arguments

	cmd = ns.core.CommandLine()

	cmd.packetSize = 1024
	cmd.packetCount = 10
	cmd.packetInterval = 1.0

	#Socket options for IPv6, currently TCLASS, HOPLIMIT, RECVTCLASS, and RECVHOPLIMIT		
	cmd.ipv6Tclass = 0
	cmd.ipv6RecvTclass = True
	cmd.ipv6Hoplimit = 0
	cmd.ipv6RecvHoplimit = True

	cmd.AddValue ("packetSize", "Packet size in bytes")
	cmd.AddValue ("packetCount", "Number of packets to send")
	cmd.AddValue ("packetInterval", "Interval between packets")
	cmd.AddValue ("ipv6Tclass", "IPV6_TCLASS")
	cmd.AddValue ("ipv6RecvTclass", "IPV6_RECVTCLASS")
	cmd.AddValue ("ipv6Hoplimit", "IPV6_HOPLIMIT")
	cmd.AddValue ("ipv6RecvHoplimit", "IPV6_RECVHOPLIMIT")

	cmd.Parse(sys.argv)

	packetSize = int(cmd.packetSize)
	packetCount = int(cmd.packetCount)
	packetInterval = float(cmd.packetInterval)
	ipv6Tclass = int(cmd.ipv6Tclass)
	ipv6RecvTclass = bool(cmd.ipv6RecvTclass)
	ipv6Hoplimit = int(cmd.ipv6Hoplimit)
	ipv6RecvHoplimit = bool(cmd.ipv6RecvHoplimit)

	print "Create nodes."
	n = ns.network.NodeContainer()
	n.Create(2)

	internet = ns.internet.InternetStackHelper()
	internet.Install(n)

	print "Create channels."
	csma = ns.csma.CsmaHelper()
	csma.SetChannelAttribute("DataRate", ns.core.StringValue("5000000"))
	csma.SetChannelAttribute("Delay", ns.core.TimeValue(ns.core.MilliSeconds(2)))
	csma.SetDeviceAttribute ("Mtu", ns.core.UintegerValue (1400));

	d = csma.Install (n);

	print "Assign IP Addresses."
	ipv6 = ns.internet.Ipv6AddressHelper()
	ipv6.SetBase(ns.network.Ipv6Address("2001:0000:f00d:cafe::"), ns.network.Ipv6Prefix (64))
	i6 = ipv6.Assign (d);
	serverAddress = ns.network.Address(i6.GetAddress (1,1))

	print "Create sockets."
	#Receiver socket on n1
	tid = ns3.TypeId.LookupByName ("ns3::UdpSocketFactory")
	recvSink = ns3.Socket.CreateSocket (n.Get (1), tid)

	local = ns3.Inet6SocketAddress (ns3.Ipv6Address.GetAny (), 4477)
	recvSink.SetIpv6RecvTclass (ipv6RecvTclass)
	recvSink.SetIpv6RecvHopLimit (ipv6RecvHoplimit)
	recvSink.Bind(local)
	recvSink.SetRecvCallback (ReceivePacket)

	#Sender socket on n0
	source = ns3.Socket.CreateSocket (n.Get (0), tid)
	remote = ns3.Inet6SocketAddress (i6.GetAddress (1,1), 4477)

	#Set socket options, it is also possible to set the options after the socket has been created/connected.
	if ipv6Tclass != 0:
		source.SetIpv6Tclass (ipv6Tclass)

	if ipv6Hoplimit > 0:
		source.SetIpv6HopLimit (ipv6Hoplimit)

	source.Connect (remote)

	ascii = ns.network.AsciiTraceHelper()
	csma.EnableAsciiAll (ascii.CreateFileStream("socket-options-ipv6.tr"));
	csma.EnablePcapAll ("socket-options-ipv6", False);

	#Schedule SendPacket
	interPacketInterval = ns.core.Seconds(packetInterval)
	ns.core.Simulator.ScheduleWithContext (source.GetNode ().GetId (),ns.core.Seconds (1.0), SendPacket, source, packetSize, packetCount, interPacketInterval)

	print "Run Simulation."
	ns.core.Simulator.Run()
	ns.core.Simulator.Destroy()
	print "Done."

if __name__ == '__main__':
    main (sys.argv)



