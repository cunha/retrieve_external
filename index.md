A lot of datasets go into bdrmapIT’s inferences.
All of it can be retrieved using the retrieve_external package, but it is not necessary to use it for some or all of the datasets. The examples here assume that the retrieve_externalpackage is use.
To clone it and install required packages,
```bash
git clone https://github.com/alexmarder/retrieve-external
cd retrieve -external
pip install -r requirements.txt
```
retrieve_external also requires [traceutils](https://github.com/alexmarder/traceutils), so make sure to install that first.

The primary file retrieve.py has several arguments:

Argument | Required | Description
:---|:---|:---
-b, --begin | Required | Beginning date.
-e, --end | Optional | Ending date. If not provided, defaults to the beginning date.
-u, --username | Optional | Username if the retrieval requires a login.
-p, --password | Optional | Password, if the retrieval requires a login.
-n, –processes | Optional | Number of simultaneous downloads. Some sites prevent many simultaneous downloads to the same IP address. Defaults to 5.
-d, --dir | Required | Directory where all downloaded files will be stored. The directory will be created if it does not exist.
mode | Required | Exactly one of the choices: <ul><li>caida-team – CAIDA team probing warts files</li><li>caida-prefix – CAIDA prefix probing warts files</li><li>caida-prefix – CAIDA prefix probing warts files</li><li>bgp – RIBs from RouteViews and RIPE RIS</li><li>rir – RIR extended delegation files</li><li>rels – CAIDA AS relationships and customer cone datasets</li><li>peeringdb – PeeringDB json file from CAIDA</li></ul>

# Prefix to AS
There are several sources of data that enable the creation of prefix to AS mappings.

## BGP Route Announcements
Any route announcement will work, but I have been using the BGP route announcements from RouteViews and RIPE. A CAIDA prefix2as file can be provided later instead of creating a similar file from the raw announcements, but I’ve found that it’s incomplete. The RIB files can be retrieved by,
```bash
./retrieve.py -b <start> -e <end> -d ribs bgp
```

## RIR Extended Delegations
RIR extended delegations help provide prefixes that are missing from BGP announcements. The extended delegations contain Organization identifiers that enable matching prefixes to ASes.
```bash
./retrieve.py -b <start> -e <end> -d rirs rir
```

## AS Relationships
AS relationships are used for creating prefix-to-AS mappings and for the actual inferences. bdrmapIT requires two files, one that indicates relationships (either provider-customer or peer), and one that indicates the customer cone for an AS. The customer cone is all direct and transitive customers of an AS. Only one file can be used at a time.
```bash
./retrieve.py -b <start> -e <end> -d rels rels
```

## IXP Prefixes
PeeringDB provides prefixes used for public peering at IXPs, and even the specific IP addresses used by individual networks. It is not complete, but the information contained is highly accurate and seems to be pretty well updated. CAIDA now maintains daily snapshots of the PeeringDB database. Only one file can be used at a time.
```bash
./retrieve.py -b <start> -e <end> -d ixps peeringdb
```

# Traceroute Files
If desired, it is possible to retrieve the traceroutes CAIDA generates through its team and prefix probing. All other traceroute files, including RIPE ATLAS, must be retrieved in some other fashion.
```bash
# Team probing
./retrieve.py -b <start> -e <end> -d team caida-team
# Prefix probing
./retrieve.py -b <start> -e <end> -d team caida-prefix
```