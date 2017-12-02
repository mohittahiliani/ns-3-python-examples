# /* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
# /*
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License version 2 as
# * published by the Free Software Foundation;
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# */

#  Network topology
#
#         n0              n1
#          |               |
#         =================
#                LAN
#
#   - UDP flows from n0 to n1

import ns3
import ns.core
import ns.csma
import ns.applications
import ns.internet
import ns.network
import sys

def ReceivePacket(socket):

    print "Received one packet!"
    packet = socket.Recv ()

    tosTag = ns3.socket.SocketIpTosTag ()
    if packet.RemovePacketTag (tosTag) == True:
        print "TOS = ", tosTag.GetTos ()

    ttlTag = ns3.socket.SocketIpTtlTag ()
    if packet.RemovePacketTag (ttlTag) == True:
        print "TTL = ", ttlTag.GetTos ()

def SendPacket (args,socket, pktSize, pktCount, pktInterval ):

    if pktCount > 0:
        print "packet sent"
        p = ns.network.Packet(pktSize)
        socket.Send (p)
        ns.core.Simulator.Schedule (pktInterval, SendPacket,"args", socket, pktSize,pktCount - 1, pktInterval)

    else:
        socket.Close ()

def main(argv):

    #
    # Allow the user to override any of the defaults and the above Bind() at
    # run-time, via command-line arguments
    #
    cmd = ns.core.CommandLine ()
    cmd.packetSize = 1024
    cmd.packetCount = 10
    cmd.packetInterval = 1.0

    #
    # Socket options for IPv4, currently TOS, TTL, RECVTOS, and RECVTTL
    #
    cmd.ipTos = 0
    cmd.ipRecvTos = True
    cmd.ipTtl = 0
    cmd.ipRecvTtl = True
    cmd.AddValue ("PacketSize", "Packet size in bytes")
    cmd.AddValue ("PacketCount", "Number of packets to send")
    cmd.AddValue ("Interval", "Interval between packets")
    cmd.AddValue ("IP_TOS", "IP_TOS")
    cmd.AddValue ("IP_RECVTOS", "IP_RECVTOS")
    cmd.AddValue ("IP_TTL", "IP_TTL")
    cmd.AddValue ("IP_RECVTTL", "IP_RECVTTL")
    cmd.Parse (sys.argv)

    packetSize = int(cmd.packetSize)
    packetCount = int(cmd.packetCount)
    packetInterval = float(cmd.Interval)
    IP_TOS = int(cmd.IP_TOS)
    IP_RECVTOS = bool(cmd.IP_RECVTOS)
    IP_TTL = int(cmd.IP_TTL)
    IP_RECVTTL = bool(cmd.IP_RECVTTL)

    print "Create nodes"
    n = ns.network.NodeContainer ()
    n.Create (2)

    internet = ns.internet.InternetStackHelper ()
    internet.Install (n)

    serverAddress = ns.network.Address

    print "Create channels."
	csma = ns.csma.CsmaHelper ()
	csma.SetChannelAttribute ("DataRate", ns.core.StringValue ("5000000"))
	csma.SetChannelAttribute ("Delay", ns.core.TimeValue (ns.core.MilliSeconds (2)))
	csma.SetDeviceAttribute ("Mtu", ns.core.UintegerValue (1400))
	d = csma.Install (n)

	print "Assign IP Addresses."
    address = ns.internet.Ipv4AddressHelper ()
    address.SetBase (ns.network.Ipv4Address ("10.1.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))
    i = address.Assign (devices)
    serverAddress = ns.network.Address (i.GetAddress (1))

    print " Create sockets"

    #
    # Receiver socket on n1
    #
    tid = ns3.TypeId.LookupByName ("ns3::UdpSocketFactory")
    local = ns3.InetSocketAddress (ns3.Ipv4Address.GetAny (), 4477)

    recvSink.SetIpRecvTos (ipRecvTos);
    recvSink.SetIpRecvTtl (ipRecvTtl);
    recvSink.Bind (local);
    recvSink.SetRecvCallback (ReceivePacket);

    #
    # sender socket on n0
    #
    source = ns3.Socket.CreateSocket (n.Get (0), tid)
    remote = ns3.InetSocketAddress (i.GetAddress(1), 4477)

    #
    # Set socket options, it is also possible to set the options after the socket has been created/connected.
    #
    if ipTos > 0 :
          source.SetIpTos (ipTos)

    if (ipTtl > 0):
          source.SetIpTtl (ipTtl)

    source.Connect (remote)

    ascii = ns.network.AsciiTraceHelper ()
    csma.EnableAsciiAll (ascii.CreateFileStream ("socket-options-ipv4.tr"))
    csma.EnablePcapAll ("socket-options-ipv4", false)

    #
    # Schedule send packet
    #
    interPacketInterval = ns.core.Seconds (packetInterval)
    ns.core.Simulator.ScheduleWithContext (source.GetNode ().GetId (), ns.core.Seconds (1.0), &SendPacket,source, packetSize, packetCount, interPacketInterval)

    print "Run Simulation."
	ns.core.Simulator.Run ()
	ns.core.Simulator.Destroy ()
	print "Done."

    if __name__ == '__main__':
        import sys
        main (sys.argv)
