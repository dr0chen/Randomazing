from game import *

init()

while True:

    poll_event()
    update()
    render()
    
    glob_var["clock"].tick(60)