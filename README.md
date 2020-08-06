# S7Client
Usage: ```python s7client.py <IP>/<RACK>/<SLOT> <DB>.<OFFSET>.<LENGTH IN BYTES>```

Example: ```python s7client.py 192.168.0.7/0/2 45.0.4 ``` will read from PLC at IP 192.168.0.7, at RACK 0, SLOT 2 and Datablock 45 will be requested starting at offset 0 and reading 4 bytes.

Note: The supplied value for _rack_ is ignored for now. It doesn't seem to be widely used anyway.
