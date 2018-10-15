# Arango Performance Tester

Code to populate arangodb with large amounts of data and test query performance.
We're going to test latest arango version (3.3) using rocksdb backend.

## Setup

Ref: Arango Server Configuration:
https://docs.arangodb.com/3.3/Manual/Administration/Configuration/OperatingSystem.html

```bash
sudo bash -c "echo madvise >/sys/kernel/mm/transparent_hugepage/enabled"
sudo bash -c "echo madvise >/sys/kernel/mm/transparent_hugepage/defrag"
sudo bash -c "echo 2 >/proc/sys/vm/overcommit_memory"
sudo bash -c "echo 90 > /proc/sys/vm/overcommit_ratio"
sudo bash -c "echo 0 >/proc/sys/vm/zone_reclaim_mode"
sudo bash -c "sysctl -w 'vm.max_map_count=256000'"
export GLIBCXX_FORCE_NEW=1
```

### Arango Installation

Ref: https://www.arangodb.com/download-major/ubuntu/

```bash
curl -OL https://download.arangodb.com/arangodb33/xUbuntu_17.04/Release.key
sudo apt-key add - < Release.key
echo 'deb https://download.arangodb.com/arangodb33/xUbuntu_17.04/ /' | sudo tee /etc/apt/sources.list.d/arangodb.list
sudo apt-get install apt-transport-https
sudo apt-get update
sudo apt-get install arangodb3=3.3.17
```

Now create a database and optionally user for the testing.

### Cluster Setup

```bash
# on tf-api
arangodb --server.storage-engine=rocksdb --starter.address=10.131.78.29 \
         --starter.data-dir=./arango_data \
         --starter.join=arrangodb-4vcpu-8gb-ams3-01,arrangodb-4vcpu-8gb-ams3-02,arrangodb-4vcpu-8gb-ams3-03

# On tf-ar01
arangodb --starter.data-dir=./arango_data --starter.join 10.131.78.29

# On tf-ar02
arangodb --starter.data-dir=./arango_data --starter.join 10.131.78.29
```

### Code Setup


```bash
apt install python3-pip
pip3 install arango-orm
```

You can adjust the connection credentials in db_credentials.py

## Creating the Graph and Models

```bash
python3 main.py create_structure
```

## Populate the models

Inserting a million random records into the logs collection.

```bash
python3 main.py populate logs 1000000
```
