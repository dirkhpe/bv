import logging
from lib import my_env
from lib import neostore

# Node Labels
# Relations
server2wave = "serverInWave"

cfg = my_env.init_env("bellavista", __file__)
logging.info("Start Application")
ns = neostore.NeoStore(cfg)
query = """
    MATCH (wave:Wave)<-[:inWave]-(sol),
    (sol)<-[:fromSolution]-(solComp),
    (solComp)<-[:toComponent]-(instComp),
    (instComp)-[:toInstance]-(inst),
    (inst)<-[:serverInst]-(server)
    return wave, sol, solComp, instComp, inst, server
"""
cursor = ns.get_query(query)
my_loop = my_env.LoopInfo("Server in Wave", 20)
while cursor.forward():
    my_loop.info_loop()
    rec = cursor.current()
    server_node = rec["server"]
    wave_node = rec["wave"]
    ns.create_relation(from_node=server_node, rel=server2wave, to_node=wave_node)
my_loop.end_loop()

"""
query =
match (s:Server)-[r:serverInWave]->()
with s, count(r) as rel_cnt
match (s)-[:serverInWave]->(wave)
where rel_cnt > 1
return s, wave
"""