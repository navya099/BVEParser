import re
class Parser:
    def preprocess_split_into_expressions(file_name, lines, allow_rw_route_description, track_position_offset=0.0):
        expressions = Expressions ()
        
        # full-line rw comments
        if is_rw:
            for i in range(len(lines)):
                level = 0
                j = 0
                while j < len(lines[i]):
                    char = lines[i][j]
                    if char == '(':
                        level += 1
                    elif char == ')':
                        level -= 1
                    elif char == ';' and level == 0:
                        lines[i] = lines[i][:j].rstrip()
                        break
                    elif char == '=' and level == 0:
                        break
                    j += 1
        
        e = 0
        for i in range(len(lines)):
            lines[i] = lines[i].replace("\0", "")
            
            if is_rw and allow_rw_route_description:
                if lines[i].startswith("[") and "]" in lines[i] or lines[i].startswith("$"):
                    allow_rw_route_description = False
                    current_route.comment = current_route.comment.strip()
                else:
                    if current_route.comment:
                        current_route.comment += "\n"
                    current_route.comment += lines[i]
                    continue
            
            n = 0
            level = 0
            for char in lines[i]:
                if char == '(':
                    level += 1
                elif char == ')':
                    level -= 1
                elif char == ',' and not is_rw and level == 0:
                    n += 1
                elif char == '@' and is_rw and level == 0:
                    n += 1
            
            if split_line_hack:
                matches = re.findall(r".Load", lines[i], re.IGNORECASE)
                if len(matches) > 1:
                    split_line = [s.strip() for s in lines[i].split(',') if s.strip()]
                    lines.pop(i)
                    for new_line in reversed(split_line):
                        lines.insert(i, new_line)
            
            a, c = 0, 0
            level = 0
            for j, char in enumerate(lines[i]):
                if char == '(':
                    level += 1
                elif char == ')':
                    level = max(0, level - 1)
                elif char == ',' and level == 0 and not is_rw:
                    t = lines[i][a:j].strip()
                    if t and not t.startswith(';'):
                        expressions.append(Expression(file_name, t, i + 1, c + 1, track_position_offset))
                        e += 1
                    a = j + 1
                    c += 1
                elif char == '@' and level == 0 and is_rw:
                    t = lines[i][a:j].strip()
                    if t and not t.startswith(';'):
                        expressions.append(Expression(file_name, t, i + 1, c + 1, track_position_offset))
                        e += 1
                    a = j + 1
                    c += 1
            
            if a < len(lines[i]):
                t = lines[i][a:].strip()
                if t and not t.startswith(';'):
                    expressions.append(Expression(file_name, t, i + 1, c + 1, track_position_offset))
                    e += 1
        
        return expressions
