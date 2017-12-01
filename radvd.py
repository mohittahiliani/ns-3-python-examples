#/* -*-  Mode: Python; -*- */
#/*
#* Copyright (c) 2017 NITK Surathkal
#*
# * This program is free software; you can redistribute it and/or modify
 #* it under the terms of the GNU General Public License version 2 as
 #* published by the Free Software Foundation;
 #*
 #* This program is distributed in the hope that it will be useful,
 #* but WITHOUT ANY WARRANTY; without even the implied warranty of
 #* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 #* GNU General Public License for more details.
 #*
 #* You should have received a copy of the GNU General Public License
 #* along with this program; if not, write to the Free Software
 #* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 #*
 #* Ported to Python by: Ritwick Mishra <ritwick0310@gmail.com>
 #*         
 #*/

#// Network topology
#// //
#// //             n0   R    n1
#// //             |    _    |
#// //             ====|_|====
#// //                router
#// // - R sends RA to n0's subnet (2001:1::/64);
#// // - R sends RA to n1's subnet (2001:2::/64);
#// // - n0 ping6 n1.
#// //
#// // - Tracing of queues and packet receptions to file "radvd.tr"



import ns.core
import ns.internet
import ns.applications
import ns.radvd
import ns.csma


print "RadvdExample"

verbose = False

cmd. ns.core.CommandLine
cmd.AddValue ("verbose", "turn on log components")
cmd.Parse (sys.argv)
if verbose:
  
  ns.core.LogComponentEnable ("Ipv6L3Protocol", ns.core.LOG_LEVEL_ALL)
  ns.core.LogComponentEnable ("Ipv6RawSocketImpl", ns.core.LOG_LEVEL_ALL)
  ns.core.LogComponentEnable ("Icmpv6L4Protocol", ns.core.LOG_LEVEL_ALL)
  LogComponentEnable ("Ipv6StaticRouting", ns.core.LOG_LEVEL_ALL)
  LogComponentEnable ("Ipv6Interface", ns.core.LOG_LEVEL_ALL)
  LogComponentEnable ("RadvdApplication", ns.core.LOG_LEVEL_ALL)
  LogComponentEnable ("Ping6Application", ns.core.LOG_LEVEL_ALL)
    
print "Create nodes."
n0 = ns.network.CreateObject<Node> ()
r = ns.network.CreateObject<Node> ()
n1 = ns.network.CreateObject<Node> ()

net1 = ns.network.NodeContainer(n0, r)
net2 = ns.network.NodeContainer(r, n1)
allnet  =  ns.network.NodeContainer(n0, r, n1) # allnet is like all in cpp program

print "Create IPv6 Internet Stack"
internetv6 = ns.internet.InternetStackHelper()
internetv6.Install(all)

print "Create channels."
csma = ns.csma.CsmaHelper()
csma.SetChannelAttribute ("DataRate", DataRateValue (5000000))
csma.SetChannelAttribute ("Delay", TimeValue (MilliSeconds (2)))
d1 = csma.Install (net1) #/* n0 - R */
d2 = csma.Install (net2) #/* R - n1 */

print "Create networks and assign IPv6 Addresses."
ipv6 = ns.internet.Ipv6AddressHelper;

#/* first subnet */
ipv6.SetBase (ns.network.Ipv6Address ("2001:1::"), ns.network.Ipv6Prefix (64))
tmp = ns.network.NetDeviceContainer()
tmp.Add (d1.Get (0)) #/* n0 */
iic1 = ns.internet.Ipv6InterfaceContainer()
iic1 = ipv6.AssignWithoutAddress (tmp) #/* n0 interface */

tmp2 = ns.network.NetDeviceContainer()
tmp2.Add (d1.Get (1)) #/* R */
iicr1 = ns.internet.Ipv6InterfaceContainer() 
iicr1 = ipv6.Assign (tmp2) #/* R interface to the first subnet is just statically assigned */
iicr1.SetForwarding (0, True)
iic1.Add (iicr1)
#/* second subnet R - n1 */
ipv6.SetBase (ns.network.Ipv6Address ("2001:2::"), ns.network.Ipv6Prefix (64))

tmp3 = ns.network.NetDeviceContainer()
tmp3.Add (d2.Get (0)); #/* R */
iicr2 = ns.internet.Ipv6InterfaceContainer() 
iicr2 = ipv6.Assign (tmp3)#/* R interface */
iicr2.SetForwarding (0, True)

tmp4 = ns.network.NetDeviceContainer()
tmp4.Add (d2.Get (1)) #/* n1 */
iic2 = ns.internet.Ipv6InterfaceContainer() 
iic2 = ipv6.AssignWithoutAddress (tmp4)
iic2.Add (iicr2)

#/* radvd configuration */
radvdHelper = ns.applications.RadvdHelper ()

#/* R interface (n0 - R) */
#/* n0 will receive unsolicited (periodic) RA */
radvdHelper.AddAnnouncedPrefix (iic1.GetInterfaceIndex (1), ns.network.Ipv6Address("2001:1::0"), 64)

#/* R interface (R - n1) */
#/* n1 will have to use RS, as RA are not sent automatically */
radvdHelper.AddAnnouncedPrefix(iic2.GetInterfaceIndex (1), ns.network.Ipv6Address("2001:2::0"), 64)
radvdHelper.GetRadvdInterface (iic2.GetInterfaceIndex (1)).SetSendAdvert (False)

radvdApps = ns.network.ApplicationContainer() 
radvdApps = radvdHelper.Install (r)
radvdApps.Start (ns.coreSeconds (1.0))
radvdApps.Stop (Seconds (10.0))

#* Create a Ping6 application to send ICMPv6 echo request from n0 to n1 via R */
packetSize = 1024
maxPacketCount = 5
interPacketInterval = Time() 
interPacketInterval = Seconds (1.)
ping6 = ns.applications.Ping6Helper() 

#/* ping6.SetLocal (iic1.GetAddress (0, 1)); */
ping6.SetRemote (ns.network.Ipv6Address ("2001:2::200:ff:fe00:4")) #/* should be n1 address after autoconfiguration */
ping6.SetIfIndex (iic1.GetInterfaceIndex (0))

ping6.SetAttribute ("MaxPackets", UintegerValue (maxPacketCount))
ping6.SetAttribute ("Interval", TimeValue (interPacketInterval))
ping6.SetAttribute ("PacketSize", UintegerValue (packetSize))
apps = ns.network.ApplicationContainer() 
apps = ping6.Install (net1.Get (0))
apps.Start (Seconds (2.0))
apps.Stop (Seconds (7.0))

Ascii = ns.applications.AsciiTraceHelper ()
csma.EnableAsciiAll (Ascii.CreateFileStream ("radvd.tr"))
csma.EnablePcapAll ("radvd", True)

print ("Run Simulation.")
ns.core.Simulator.Run ()
ns.core.Simulator.Destroy ()
print ("Done.")



