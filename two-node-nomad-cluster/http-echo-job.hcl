job "http-echo" {
  datacenters = ["dc1"]
  group "echo" {
    network {
      mode = "bridge" 
      port "http" {
        static = 8080
        to = 80
      }
    }
    count = 2
    task "server" {
      driver = "docker"
      config {
        image = "nginx"
        ports = ["http"]
      }
    }
    service {
      name = "http-echo"
      port = "http"
  
      tags = [
        "macbook",
        "urlprefix-/http-echo",
      ]

      check {
        type     = "http"
        path     = "/"
        interval = "2s"
        timeout  = "2s"
      }
    }
  }
}