
import heapq
import collections
INFINITY = 1000000

def execute_sequence(pos, sequence):
    for move, cost in sequence:
        pos.move(move)

def undo_sequence(pos, sequence):
    for move, cost in reversed(sequence):
        pos.undo_move(move)

#def A(pos, limit = 25000):
#    min_heur = 99999
#    cur_move = []
#    for move, cost in pos.generate_moves():
#        pos.move(move)
#        evaluate = pos.evaluate()
#        if(evaluate < min_heur):
#            min_heur = evaluate
#            cur_move = move
#    return [(cur_move, 0)]

def A(pos, limit = 4):
    cand_paths = [(pos.evaluate(), [], pos.ID())]
    visited = { pos.ID(): (0, pos.evaluate()) }
    ix = 1
    while cand_paths:
        if ix > limit: return path    
        ix += 1
        val, path, id = heapq.heappop(cand_paths)
        execute_sequence(pos, path)
        if pos.solved():
            undo_sequence(pos, path)
            return path
        if visited[id][1] < val:
            undo_sequence(pos, path)
            continue
        for move, cost in pos.generate_moves():
            pos.move(move)
            new_id = pos.ID()
            if new_id not in visited or visited[new_id][0] > visited[id][0] + cost:
                visited[new_id] = (visited[id][0] + cost, visited[id][0] + cost + pos.evaluate())
                heapq.heappush(cand_paths, (visited[new_id][1], path + [(move, cost)], new_id))
            pos.undo_move(move)
        undo_sequence(pos, path)
    return None  




