import ns._core
import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point
import ns.point_to_point_layout

def main(argv):

    cmd = ns.core.CommandLine ()
    cmd.pNodes = 2
    cmd.numApps = 1
    cmd.tcpType = "NewReno"
    cmd.queueSize = 50000
    cmd.maxBytes = 0
    cmd.AddValue ("pNodes", "Number of left and right side leaf nodes")
    cmd.AddValue ("queueSize","Max Packets allowed in the device queue")
    cmd.AddValue ("tcpType","Tcp version to simulate")
    cmd.AddValue ("numApps", "Number of sender and receiver apps")
    cmd.AddValue ("maxBytes", "Max Bytes to tranfer")
    cmd.Parse (sys.argv)

    numLtNodes = int(cmd.pNodes)
    numRtNodes = int(cmd.pNodes)
    queueSize = int(cmd.queueSize)
    numApps = int(cmd.numApps)
    tcpType = str(cmd.tcpType)
    maxBytes = int(cmd.maxBytes)
    emwa = 0.1
    thigh= 500
    tlow= 50
    addstep= 4.0
    beta= 0.01

    ns.core.Config.SetDefault ("ns3::QueueBase::MaxPackets", ns.core.UintegerValue(queueSize))
    socketType = "ns3::TcpSocketFactory"
    if tcpType == "NewReno":
        print "Setting Default protocol to Tcp-NewReno"
        ns.core.Config.SetDefault("ns3::TcpL4Protocol::SocketType", ns.core.TypeIdValue (ns.internet.TcpNewReno.GetTypeId ()))
    elif tcpType == "Veno":
        print "Setting Default protocol to Tcp-Veno"
        ns.core.Config.SetDefault("ns3::TcpL4Protocol::SocketType", ns.core.TypeIdValue (ns.internet.TcpVeno.GetTypeId ()))
    elif tcpType == "HighSpeed":
        print "Setting Default protocol to Tcp-HighSpeed"
        ns.core.Config.SetDefault("ns3::TcpL4Protocol::SocketType", ns.core.TypeIdValue (ns.internet.TcpHighSpeed.GetTypeId ()))
    elif tcpType == "Vegas":
        print "Setting Default protocol to Tcp-Vegas"
        ns.core.Config.SetDefault("ns3::TcpL4Protocol::SocketType", ns.core.TypeIdValue (ns.internet.TcpVegas.GetTypeId ()))
    elif tcpType == "Westwood":
        print "Setting Default protocol to Tcp-Westwood"
        ns.core.Config.SetDefault("ns3::TcpL4Protocol::SocketType", ns.core.TypeIdValue (ns.internet.TcpWestwood.GetTypeId ()))
    elif tcpType == "Bic":
        print "Setting Default protocol to Tcp-Bic"
        ns.core.Config.SetDefault("ns3::TcpL4Protocol::SocketType", ns.core.TypeIdValue (ns.internet.TcpBic.GetTypeId ()))
    elif tcpType == "Timely":
        print "Setting Default protocol to Tcp-Timely"
        ns.core.Config.SetDefault("ns3::TcpL4Protocol::SocketType", ns.core.TypeIdValue (ns.internet.TcpTimely.GetTypeId ()))
        ns.core.Config.SetDefault("ns3::TcpTimely::EMWA",ns.core.DoubleValue(emwa))
        ns.core.Config.SetDefault("ns3::TcpTimely::Addstep", ns.core.DoubleValue(addstep))
        ns.core.Config.SetDefault("ns3::TcpTimely::Beta", ns.core.DoubleValue(beta))
        ns.core.Config.SetDefault("ns3::TcpTimely::THigh", ns.core.DoubleValue(thigh))
        ns.core.Config.SetDefault("ns3::TcpTimely::TLow",ns.core.DoubleValue(tlow))

    print "Building topology with required specifications"
    p2pLeaf=ns.point_to_point.PointToPointHelper()
    p2pRouters=ns.point_to_point.PointToPointHelper()
    p2pLeaf.SetDeviceAttribute     ("DataRate", ns.core.StringValue ("50Mbps"))
    p2pLeaf.SetChannelAttribute    ("Delay",    ns.core.StringValue ("1us"))
    p2pRouters.SetDeviceAttribute  ("DataRate", ns.core.StringValue ("50Mbps"))
    p2pRouters.SetChannelAttribute ("Delay",    ns.core.StringValue ("1us"))
    dumbbell=ns.point_to_point_layout.PointToPointDumbbellHelper(numLtNodes, p2pLeaf,numRtNodes, p2pLeaf,p2pRouters)

    print "Installing Internet stack on all nodes"
    stack = ns.internet.InternetStackHelper()
    dumbbell.InstallStack (stack)

    print "Assigning Ipv4 addresses to all nodes"
    ltIps = ns.internet.Ipv4AddressHelper(ns.network.Ipv4Address("10.1.1.0"),ns.network.Ipv4Mask ("255.255.255.0"))
    rtIps = ns.internet.Ipv4AddressHelper(ns.network.Ipv4Address("10.2.1.0"),ns.network.Ipv4Mask ("255.255.255.0"))
    routerIps = ns.internet.Ipv4AddressHelper(ns.network.Ipv4Address("10.3.1.0"),ns.network.Ipv4Mask ("255.255.255.0"))
    dumbbell.AssignIpv4Addresses(ltIps,rtIps,routerIps)

    port = 9
    sourceApps = ns.network.ApplicationContainer()
    sinkApps = ns.network.ApplicationContainer()

    print "Creating Applications"
    for i in range(0,numApps):
        source = ns.applications.BulkSendHelper("ns3::TcpSocketFactory",ns.network.InetSocketAddress (dumbbell.GetRightIpv4Address (0), port+i))
        source.SetAttribute("MaxBytes",ns.core.UintegerValue(maxBytes))
        sourceApps.Add(source.Install(dumbbell.GetLeft(0)))
        sourceApps.Start (ns.core.Seconds (0))
        sourceApps.Stop  (ns.core.Seconds (10.0))

        sink = ns.applications.PacketSinkHelper("ns3::TcpSocketFactory",ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), port+i))
        sinkApps.Add(sink.Install(dumbbell.GetRight(0)))
        sinkApps.Start(ns.core.Seconds(0))
        sinkApps.Stop(ns.core.Seconds(0))

    ns.internet.Ipv4GlobalRoutingHelper.PopulateRoutingTables ()
    p2pLeaf.EnablePcapAll ("dumbbell-tcp-py")

    print "Simulation started"
    ns.core.Simulator.Stop (ns.core.Seconds (10))
    ns.core.Simulator.Run ()
    ns.core.Simulator.Destroy ()
    print "Simulation ended"

    for i in range(0,numApps):
        measure = ns.applications.PacketSink()
        measure = sinkApps.Get(i)
        throughput = measure.GetTotalRx()
        print "Throughput : "+str(throughput)+" at port : "+str(port+i)

if __name__ == '__main__':
    import sys

main(sys.argv)
