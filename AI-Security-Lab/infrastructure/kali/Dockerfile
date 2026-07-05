# Kali attacker image with the lab's tools baked in.
# The stock kalilinux/kali-rolling image is minimal (no nmap/sqlmap/etc.), so we
# install exactly the tools the scenarios use. netcat-traditional is chosen on
# purpose: it supports `nc -e` (reverse shell in scenario 06); the openbsd variant does not.
FROM kalilinux/kali-rolling

RUN apt-get update && apt-get install -y --no-install-recommends \
      nmap \
      sqlmap \
      hydra \
      netcat-traditional \
      iodine \
      dnsutils \
      whatweb \
      curl \
      wget \
      git \
      python3 \
      python3-pip \
 && rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"]
