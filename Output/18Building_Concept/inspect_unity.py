import re,json,pathlib
from mathutils import Matrix,Vector,Quaternion
ROOT=pathlib.Path(r'C:\Users\momoii\Desktop\UnityWorkspace\XRProject_Assignment')
OUT=ROOT/'Output/18Building_Concept'
def docs(path):
    s=path.read_text(encoding='utf-8-sig')
    return {int(m[1]):(int(m[0]),m[2]) for m in re.findall(r'--- !u!(\d+) &(-?\d+)[^\n]*\n(.*?)(?=--- !u!|\Z)',s,re.S)}
def value(s,k,default=''):
    m=re.search(r'^  '+re.escape(k)+r': (.*)$',s,re.M)
    return m[1] if m else default
def ref(s,k):
    return int(re.search(r'fileID: (-?\d+)',value(s,k,'{fileID: 0}'))[1])
def vec(s,k,default):
    v=value(s,k)
    return [float(x) for x in re.findall(r'[xyzw]: ([^,}]+)',v)] if v else default
guidmap={}
for p in (ROOT/'Assets').rglob('*.meta'):
    m=re.search(r'^guid: (\w+)',p.read_text(encoding='utf-8-sig',errors='ignore'),re.M)
    if m:guidmap[m[1]]=pathlib.Path(str(p)[:-5])
scene=docs(ROOT/'Assets/Scenes/18Building.unity')
pref=docs(ROOT/'Assets/18Map/Prefabs/Ceils/Corridor.prefab')
# Apply scene overrides to source prefab records before hierarchy resolution.
for typ,s in scene.values():
    if typ!=1001 or 'guid: 91e2e3083af55e349beb1c2f249a6cd7' not in s:continue
    for tid,key,val in re.findall(r'- target: \{fileID: (\d+)[^\n]*\n\s+propertyPath: ([^\n]+)\n\s+value: ([^\n]*)',s):
        tid=int(tid)
        if tid not in pref:continue
        t,b=pref[tid]
        if '.' in key and key.split('.')[0] in ['m_LocalPosition','m_LocalRotation','m_LocalScale']:
            field,axis=key.split('.')
            b=re.sub(r'('+field+r': \{[^\n]*?\b'+axis+r': )[^,}]+',lambda m:m[1]+val,b)
        elif key=='m_Name': b=re.sub(r'm_Name: [^\n]*','m_Name: '+val,b)
        pref[tid]=(t,b)
def collect(data,base=Matrix.Identity(4),prefix='',depth=0):
    gos={i:s for i,(t,s) in data.items() if t==1}
    trs={i:s for i,(t,s) in data.items() if t==4 and value(s,'m_LocalPosition')}
    bygo={ref(s,'m_GameObject'):i for i,s in trs.items()}
    cache={}
    def world(i):
        if i in cache:return cache[i]
        s=trs[i];p=vec(s,'m_LocalPosition',[0,0,0]);q=vec(s,'m_LocalRotation',[0,0,0,1]);sc=vec(s,'m_LocalScale',[1,1,1])
        mat=Matrix.LocRotScale(Vector(p),Quaternion((q[3],q[0],q[1],q[2])),Vector(sc))
        father=ref(s,'m_Father')
        cache[i]=(world(father) if father in trs else base)@mat
        return cache[i]
    def ancestry(i):
        s=trs[i];n=value(gos.get(ref(s,'m_GameObject'),''),'m_Name');f=ref(s,'m_Father')
        return (ancestry(f)+'/' if f in trs else prefix)+n
    for i,(t,s) in data.items():
        if t!=33:continue
        go=ref(s,'m_GameObject');tr=bygo.get(go)
        if not tr:continue
        mesh=value(s,'m_Mesh');mid=int(re.search(r'fileID: (-?\d+)',mesh)[1]);name=ancestry(tr)
        yield dict(name=name,mesh=mid,matrix=[list(row) for row in world(tr)],asset=str(guidmap.get(re.search(r'guid: (\w+)',mesh)[1],'')))
    if depth>3:return
    for i,(t,s) in data.items():
        if t!=1001:continue
        m=re.search(r'm_SourcePrefab: .*guid: (\w+)',s)
        path=guidmap.get(m[1]) if m else None
        if not path or path.suffix!='.prefab':continue
        child=docs(path)
        for tid,key,val in re.findall(r'- target: \{fileID: (\d+)[^\n]*\n\s+propertyPath: ([^\n]+)\n\s+value: ([^\n]*)',s):
            tid=int(tid)
            if tid not in child:continue
            ct,b=child[tid]
            if '.' in key and key.split('.')[0] in ['m_LocalPosition','m_LocalRotation','m_LocalScale']:
                field,axis=key.split('.')
                b=re.sub(r'('+field+r': \{[^\n]*?\b'+axis+r': )[^,}]+',lambda m:m[1]+val,b)
            elif key=='m_Name':b=re.sub(r'm_Name: [^\n]*','m_Name: '+val,b)
            child[tid]=(ct,b)
        parent=ref(s,'m_TransformParent')
        yield from collect(child,world(parent) if parent in trs else base,prefix+path.stem+'/',depth+1)
items=list(collect(pref))
(OUT/'unity_geometry.json').write_text(json.dumps(items,indent=2),encoding='utf-8')
for o in items:
    mat=Matrix(o['matrix']);p=mat.translation;sc=mat.to_scale()
    print(o['name'],o['mesh'],[round(v,2) for v in p],[round(v,2) for v in sc],o['asset'])
print('COUNT',len(items))
