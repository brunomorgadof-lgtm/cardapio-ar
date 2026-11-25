exec(open('align.py').read().split("A = cams['A']")[0])
A = cams['A']; b0=np.degrees(A['phi'])
b = search('185010', A, np.radians([b0-3,b0,b0+3]), [-30,-15,0,15,30], [0.96,1,1.04,1.08], np.radians([-4,0,4]))
print('A', b[0], np.degrees(b[1]['phi']), np.degrees(b[1]['psi']), b[1]['cy']-A['cy'], b[1]['s']/A['s'])
b = search('185010', b[1], [b[1]['phi']], [-10,0,10], [0.985,1,1.015], np.radians([-2,0,2]))
print('A fino', b[0])
cams['A'] = b[1]
json.dump({k:{kk:float(vv) for kk,vv in c.items()} for k,c in cams.items()}, open('cams.json','w'))
