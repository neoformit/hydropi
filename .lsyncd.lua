-- $ sudo apt install lsyncd
-- $ ./sync  # One-way sync to remote


-- Add sync config here

HOST     = "raspberrypi.local"
USER     = "pi"             -- Remote user
SRC_DIR  = "/home/cameron/dev/hydro/hydropi/"   -- Trailing slash syncs dir contents only
DEST_DIR = "/home/pi/hydro/hydropi"
RSA_KEY  = "~/.ssh/neoform.pem"
EXCLUDE  = { '.git' , 'sync', '.lsyncd.lua', 'nohup.out', '*.log', 'config.yml'}


-- Shouldn't need to touch this:

settings {
    logfile = "/var/log/lsyncd/lsyncd.log",
    statusFile = "/var/log/lsyncd/lsyncd-status.log",
    statusInterval = 20
}

sync {
  default.rsyncssh,
  delay = 3,                    -- Sync delay after file change
  host = HOST,
  source = SRC_DIR,
  targetdir = DEST_DIR,
  exclude = EXCLUDE,
  rsync = {
    rsh = "/usr/bin/ssh -l " .. USER .. " -i " .. RSA_KEY
  }
}
