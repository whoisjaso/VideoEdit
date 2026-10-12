"""Minimal RIFX/FFX walker: prints the property tree (match names), static values (cdat doubles) and keyframe counts."""
import struct, sys
def walk(b, o, end, d, out):
    while o + 8 <= end:
        cid = b[o:o+4].decode('latin1'); sz = struct.unpack('>I', b[o+4:o+8])[0]; s = o + 8
        if cid == 'LIST':
            typ = b[s:s+4].decode('latin1'); out.append((d, 'LIST', typ, None)); walk(b, s + 4, s + sz, d + 1, out)
        else:
            data = b[s:s+sz]
            if cid == 'tdmn': out.append((d, 'name', data.split(b'\0')[0].decode('latin1'), None))
            elif cid == 'cdat': out.append((d, 'cdat', [round(x, 3) for x in struct.unpack('>' + 'd' * (len(data) // 8), data[:len(data)//8*8])], None))
            elif cid == 'lhd3': n = struct.unpack('>H', data[10:12])[0] if len(data) >= 12 else -1; out.append((d, 'lhd3', n, data[:24].hex()))
            elif cid == 'ldat': out.append((d, 'ldat', len(data), data))
            elif cid in ('tdb4',): out.append((d, cid, len(data), data))
            elif cid in ('Utf8',): out.append((d, 'utf8', data.decode('utf8', 'replace')[:80], None))
        o = s + sz + (sz & 1)
b = open(sys.argv[1], 'rb').read(); out = []; walk(b, 12, len(b), 0, out)
for d, k, v, x in out:
    if k == 'name' and v in ('ADBE Group End',): continue
    if k in ('name', 'cdat', 'utf8'): print('  ' * d + f'{k}: {v}')
    elif k == 'lhd3': print('  ' * d + f'KEYFRAMES lhd3 count={v}')
