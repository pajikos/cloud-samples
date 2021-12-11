# Full configuration options can be found at https://www.nomadproject.io/docs/configuration

#region     = "global"
#datacenter = "azure"

data_dir = "/opt/nomad/data"
bind_addr = "0.0.0.0"
name = "nomad2"

#addresses {
  # Defaults to the first private IP address.
#  http = "172.16.88.99"
#  rpc  = "172.16.88.99"
#  serf = "172.16.88.99"
#}

advertise {
  # Defaults to the first private IP address.
  http = "172.16.88.99"
  rpc  = "172.16.88.99"
  serf = "172.16.88.99"
}

client {
  enabled = true
  #network_interface = 
  servers = ["172.16.88.1"]
}

plugin "raw_exec" {
  config {
    enabled = true
  }
}

consul {
  address = "127.0.0.1:8500"
}

