# Full configuration options can be found at https://www.nomadproject.io/docs/configuration

data_dir = "/opt/nomad/data"
bind_addr = "0.0.0.0"

name = "nomad1"
#addresses {
  # Defaults to the first private IP address.
#  http = "172.16.88.1"
#  rpc  = "172.16.88.1"
#  serf = "172.16.88.1"
#}

advertise {
  # Defaults to the first private IP address.
  http = "172.16.88.1"
  rpc  = "172.16.88.1"
  serf = "172.16.88.1"
}

server {
  # license_path is required as of Nomad v1.1.1+
  #license_path = "/etc/nomad.d/nomad.hcl"
  enabled = true
  bootstrap_expect = 1
}

client {
  enabled = true
  servers = ["127.0.0.1"]
}

plugin "raw_exec" {
  config {
    enabled = true
  }
}
