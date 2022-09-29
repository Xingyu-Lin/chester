from chester.logger import *


info("hi")
debug("shouldn't appear")
set_level(DEBUG)
debug("should appear")
dir = "/tmp/testlogging"
if os.path.exists(dir):
    shutil.rmtree(dir)
configure(dir=dir)
logkv("a", 3)
logkv("b", 2.5)
dumpkvs()
logkv("b", -2.5)
logkv("a", 5.5)
dumpkvs()
info("^^^ should see a = 5.5")
logkv_mean("b", -22.5)
logkv_mean("b", -44.4)
logkv("a", 5.5)
dumpkvs()
info("^^^ should see b = 33.3")

logkv("b", -2.5)
dumpkvs()

logkv("a", "longasslongasslongasslongasslongasslongassvalue")
dumpkvs()