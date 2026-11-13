# -*- coding: utf-8 -*-
"""把 4 个独立页面改造成「单页 Tab 菜单工作台」。

- index.html  -> Tab 容器（hash 路由 / 懒加载 iframe / 高度自适应 / 章节导航）
- 原 index.html 内容另存 analysis.html
- 四个子页注入 embed 模式：隐藏自身导航、把模块互链 / 锚点交给父页接管
"""
import os
import re
import json
import html
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TABS = [
    {"key": "analysis",  "url": "analysis.html",  "num": "01", "name": "总览看板",
     "desc": "四维信号 · 趋势 · TOP100 客户 · 数据核验"},
    {"key": "segments",  "url": "segments.html",  "num": "02", "name": "细分市场",
     "desc": "乘用车 / 商用车 / 房车 / 新能源 等 6 大赛道"},
    {"key": "quotation", "url": "quotation.html", "num": "03", "name": "报价计算器",
     "desc": "EXW / FOB / CIF / DDP 实时落地成本"},
    {"key": "rules",     "url": "rules.html",     "num": "04", "name": "出口规则说明",
     "desc": "中俄两侧流程 · 单证 · 合规 · 检查清单"},
]

EMBED_CSS = """
<style id="ru-embed-css">
html.embedded nav{display:none!important}
html.embedded header{padding-top:26px!important}
html.embedded .wrap{padding-bottom:46px}
html.embedded .form-panel{position:static!important;max-height:none!important;overflow:visible!important}
</style>
"""

EMBED_JS = """
<script id="ru-embed-js">
(function(){
  if(!/[?&]embed=1(?:&|$)/.test(location.search)) return;
  document.documentElement.classList.add('embedded');
  function keyOf(href){
    var m=/(?:^|\\/)(index|analysis|segments|quotation|rules)\\.html/.exec(href);
    return m ? (m[1]==='index'?'analysis':m[1]) : null;
  }
  document.addEventListener('click',function(e){
    var t=e.target;
    while(t && t!==document && t.tagName!=='A') t=t.parentNode;
    if(!t || t.tagName!=='A') return;
    var href=t.getAttribute('href')||'';
    if(href.charAt(0)==='#'){
      e.preventDefault();
      parent.postMessage({ruTabAnchor:href.slice(1)},'*');
      return;
    }
    if(/^https?:/i.test(href)||/^mailto:/i.test(href)) return;
    if(/\\.html(?:\\?|#|$)/.test(href)){
      var k=keyOf(href);
      if(k){e.preventDefault();parent.postMessage({ruTabGo:k},'*');}
    }
  },true);
  window.addEventListener('load',function(){parent.postMessage({ruTabReady:true},'*');});
})();
</script>
"""


def patch_child(src, fname):
    """复制/改写子页：总览指向 analysis.html，增加 Tab 首页入口，注入 embed 片段。"""
    s = open(os.path.join(ROOT, src), encoding='utf-8').read()
    if 'id="ru-embed-js"' in s and '⌂ Tab 首页' in s:
        return len(s)  # 已处理过，保持幂等
    # 1) 导航中的「总览看板」改指向 analysis.html（原 index.html 已是 Tab 容器）
    s = s.replace('<a class="ptab on" href="index.html">总览看板</a>',
                  '<a class="ptab on" href="analysis.html">总览看板</a>')
    s = s.replace('<a class="ptab" href="index.html">总览看板</a>',
                  '<a class="ptab" href="analysis.html">总览看板</a>')
    # 正文里若有「返回总览」之类链接，一并指向 analysis.html
    s = re.sub(r'(<a[^>]+href=")index\.html("[^>]*>)', r'\1analysis.html\2', s)
    # 2) 导航栏首位加「Tab 首页」
    s = s.replace('<nav><div class="wrap">',
                  '<nav><div class="wrap"><a class="ptab" href="index.html">⌂ Tab 首页</a>', 1)
    # 3) 注入 embed CSS / JS（幂等）
    if 'id="ru-embed-css"' not in s:
        s = s.replace('</head>', EMBED_CSS + '</head>', 1)
    if 'id="ru-embed-js"' not in s:
        s = s.replace('</body>', EMBED_JS + '</body>', 1)
    open(os.path.join(ROOT, fname), 'w', encoding='utf-8').write(s)
    return len(s)


TAB_BUTTONS = "\n".join(
    '<button class="tab%s" data-key="%s" type="button"><span class="num">%s</span>'
    '<span class="tt"><b>%s</b><i>%s</i></span></button>' % (
        ' on' if t['key'] == 'analysis' else '', t['key'], t['num'],
        html.escape(t['name']), html.escape(t['desc']))
    for t in TABS)

FRAMES = "\n".join(
    '<iframe class="frame" id="f-%s" data-src="%s?embed=1" title="%s" '
    'scrolling="no" loading="eager"></iframe>' % (t['key'], t['url'], html.escape(t['name']))
    for t in TABS)

FOOTER_LINKS = " · ".join(
    '<a href="%s" target="_blank" rel="noopener">%s</a>' % (t['url'], html.escape(t['name']))
    for t in TABS)

SHELL = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="俄罗斯汽车出口平行进口情报工作台：总览看板、细分市场、报价计算器、出口规则说明，四个模块一个入口。">
<title>俄罗斯汽车出口 · 平行进口情报工作台</title>
<style>
:root{--bg:#0d141d;--panel:#151f2b;--panel2:#1b2836;--line:#2b3a4b;--text:#e6eef7;--muted:#8fa3b8;
--a1:#4d9cff;--a2:#34c9a1;--a3:#f2b35e;--a4:#b78bff}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--text);
 font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Arial Unicode MS",sans-serif;
 line-height:1.75;font-size:15px}
a{color:var(--a1);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:1280px;margin:0 auto;padding:0 28px}
.apphead{padding:38px 0 24px;border-bottom:1px solid var(--line);
 background:radial-gradient(900px 260px at 12% -40%,rgba(77,156,255,.16),transparent 70%)}
.eyebrow{font-size:12px;letter-spacing:1.6px;color:var(--a2);font-weight:700;text-transform:uppercase}
.eyebrow span{color:var(--muted);font-weight:500;letter-spacing:.4px;margin-left:10px;text-transform:none}
h1{font-size:34px;margin:10px 0 6px;letter-spacing:-.5px;line-height:1.3}
.sub{color:var(--muted);margin:0;font-size:14px}
.stickyhead{position:sticky;top:0;z-index:60;background:rgba(13,20,29,.96);
 backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.tabbar{display:flex;gap:10px;overflow-x:auto;scrollbar-width:thin;padding:12px 0 10px}
.tabbar::-webkit-scrollbar{height:5px}
.tabbar::-webkit-scrollbar-thumb{background:var(--line);border-radius:5px}
.tab{flex:0 0 auto;display:flex;align-items:center;gap:11px;text-align:left;cursor:pointer;
 background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:9px 16px;color:var(--muted);
 font-family:inherit;transition:border-color .15s,background .15s,transform .15s}
.tab:hover{border-color:var(--a1);transform:translateY(-1px)}
.tab.on{background:rgba(77,156,255,.14);border-color:var(--a1);color:var(--text);
 box-shadow:0 0 0 1px rgba(77,156,255,.2) inset}
.tab .num{font-size:11px;font-weight:800;letter-spacing:1px;color:var(--a2);
 background:rgba(52,201,161,.12);border-radius:7px;padding:3px 7px}
.tab.on .num{color:#9ec8ff;background:rgba(77,156,255,.18)}
.tab .tt{display:flex;flex-direction:column;line-height:1.35}
.tab .tt b{font-size:14.5px;color:inherit}
.tab .tt i{font-style:normal;font-size:11.5px;color:var(--muted);white-space:nowrap}
.subbar{display:flex;align-items:center;gap:14px;border-top:1px solid var(--line);padding:8px 0 9px;min-height:44px}
.chips{display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;flex:1}
.chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;cursor:pointer;background:transparent;border:1px solid transparent;border-radius:8px;
 color:var(--muted);font-family:inherit;font-size:12.5px;padding:4px 10px;white-space:nowrap}
.chip:hover{color:var(--a1);border-color:var(--line)}
.chip.on{color:#9ec8ff;background:rgba(77,156,255,.13);border-color:rgba(77,156,255,.4)}
.tools{display:flex;gap:7px;flex:0 0 auto}
.tool{cursor:pointer;background:var(--panel2);border:1px solid var(--line);border-radius:8px;
 color:var(--muted);font-family:inherit;font-size:12px;padding:5px 10px;white-space:nowrap}
.tool:hover{color:var(--a1);border-color:var(--a1)}
.stage{padding-top:6px;position:relative;min-height:420px}
.frame{display:none;width:100%;border:0;background:var(--bg);overflow:hidden}
.frame.on{display:block}
.loading{color:var(--muted);font-size:13px;padding:26px 0;display:none}
.loading.on{display:block}
footer{border-top:1px solid var(--line);margin-top:34px;padding:20px 0 34px;color:var(--muted);font-size:12px}
footer b{color:var(--text)}
@media(max-width:760px){
 .wrap{padding:0 14px}.apphead{padding:26px 0 18px}h1{font-size:25px}
 .tab{padding:8px 12px}.tab .tt i{display:none}.subbar{flex-wrap:wrap}
 .tools{width:100%;overflow-x:auto}
}
@media print{.stickyhead,.apphead,.loading,footer{display:none!important}
 .frame.on{display:block!important}.wrap{max-width:none;padding:0}}
</style>
</head>
<body id="ru-tab-shell">
<div class="apphead"><div class="wrap">
  <div class="eyebrow">Eastar Motors · Russia Market Workbench <span>Tab 版 v4 · 更新于 2026-11-13</span></div>
  <h1>俄罗斯汽车出口 · 平行进口情报工作台</h1>
  <p class="sub">四个模块，一个入口：点上方菜单原地切换，不跳页、不丢计算参数。支持直接分享某个 Tab 的链接。</p>
</div></div>

<div class="stickyhead">
  <div class="wrap"><div class="tabbar" id="tabbar">
__TAB_BUTTONS__
  </div></div>
  <div class="wrap"><div class="subbar">
    <div class="chips" id="chips"></div>
    <div class="tools">
      <button class="tool" id="btnTop" type="button">↑ 顶部</button>
      <button class="tool" id="btnReload" type="button">↻ 刷新本页</button>
      <button class="tool" id="btnPrint" type="button">⎙ 打印本页</button>
      <button class="tool" id="btnOpen" type="button">↗ 独立打开</button>
    </div>
  </div></div>
</div>

<div class="wrap stage">
  <div class="loading on" id="loading">正在载入模块…</div>
__FRAMES__
</div>

<footer><div class="wrap">
  <b>独立页面（可直接访问 / 打印 / 分享）：</b>__FOOTER_LINKS__<br>
  数据口径与免责说明见各模块「数据来源 / 核验」章节；关单样本为 5000 行官方直采基准盘，结论请结合最新政策复核。
</div></footer>

<script>
(function(){
  var MAP=__TABMAP__;
  var buttons=[].slice.call(document.querySelectorAll('#tabbar .tab'));
  var chips=document.getElementById('chips');
  var loading=document.getElementById('loading');
  var active='analysis', loaded={}, currentChip='';

  function frame(k){return document.getElementById('f-'+k)}
  function headH(){return document.querySelector('.stickyhead').offsetHeight+14}

  function fit(k){
    var f=frame(k);
    try{
      var d=f.contentDocument; if(!d||!d.body) return 0;
      var h=Math.max(d.body.scrollHeight,d.documentElement.scrollHeight);
      if(h>200) f.style.height=(h+30)+'px';
      return h;
    }catch(e){return 0}
  }

  function buildChips(k){
    var f=frame(k), out=[];
    try{
      var d=f.contentDocument; if(!d) return;
      [].forEach.call(d.querySelectorAll('nav .wrap a[href^="#"]'),function(a){
        var h=a.getAttribute('href').slice(1);
        if(h) out.push('<button class="chip" data-h="'+h+'" type="button">'+a.textContent+'</button>');
      });
    }catch(e){}
    chips.innerHTML=out.join('');
    [].forEach.call(chips.querySelectorAll('.chip'),function(b){
      b.addEventListener('click',function(){scrollAnchor(b.getAttribute('data-h'));markChip(b.getAttribute('data-h'))});
    });
    markChip(currentChip);
  }
  function markChip(h){
    currentChip=h||'';
    [].forEach.call(chips.querySelectorAll('.chip'),function(b){
      b.classList.toggle('on',b.getAttribute('data-h')===currentChip);
    });
  }
  function scrollAnchor(h){
    if(!h) return;
    var f=frame(active);
    try{
      var d=f.contentDocument,el=d.getElementById(h)||d.querySelector('[name="'+h+'"]');
      if(!el) return;
      var y=f.getBoundingClientRect().top+window.scrollY+el.getBoundingClientRect().top-headH();
      window.__lastScrollY=y;
      window.scrollTo({top:Math.max(0,y),behavior:'smooth'});
      setTimeout(function(){
        if(Math.abs(window.scrollY-Math.max(0,y))>90) window.scrollTo(0,Math.max(0,y));
      },700);
    }catch(e){}
  }

  function show(k,push){
    if(!MAP[k]) k='analysis';
    var changed=(k!==active);
    active=k;
    buttons.forEach(function(b){b.classList.toggle('on',b.getAttribute('data-key')===k)});
    Object.keys(MAP).forEach(function(x){
      var f=frame(x);
      if(x===k){
        f.classList.add('on');
        if(!loaded[x]){
          loaded[x]=true;
          loading.classList.add('on');
          f.src=f.getAttribute('data-src');
        }else{ fit(x); }
      }else{ f.classList.remove('on'); }
    });
    buildChips(k);
    if(push && location.hash!=='#/'+k) location.hash='#/'+k;
    if(changed) window.scrollTo({top:0,behavior:'auto'});
    document.title=MAP[k].name+' · 俄罗斯汽车出口情报工作台';
  }

  function onFrameLoad(k){
    var f=frame(k);
    loading.classList.remove('on');
    try{
      var d=f.contentDocument;
      if(d&&d.body&&window.ResizeObserver){
        var ro=new ResizeObserver(function(){if(active===k)fit(k)});
        ro.observe(d.body);
      }
      if(d) d.addEventListener('load',function(){if(active===k)fit(k)},true);
    }catch(e){}
    fit(k);
    setTimeout(function(){fit(k);buildChips(k)},300);
    setTimeout(function(){fit(k)},1200);
  }

  Object.keys(MAP).forEach(function(k){
    frame(k).addEventListener('load',function(){onFrameLoad(k)});
  });
  buttons.forEach(function(b){
    b.addEventListener('click',function(){markChip('');show(b.getAttribute('data-key'),true)});
  });
  window.addEventListener('hashchange',function(){
    var m=/^#\/([a-z]+)/.exec(location.hash);
    if(m) show(m[1],false);
  });
  window.addEventListener('message',function(e){
    var d=e.data||{},ok=false;
    Object.keys(MAP).forEach(function(k){if(e.source===frame(k).contentWindow)ok=true});
    if(!ok) return;
    if(d.ruTabGo){markChip('');show(d.ruTabGo,true)}
    else if(d.ruTabAnchor){scrollAnchor(d.ruTabAnchor);markChip(d.ruTabAnchor)}
    else if(d.ruTabReady){fit(active);buildChips(active)}
  });
  window.addEventListener('resize',function(){Object.keys(loaded).forEach(fit)});

  document.getElementById('btnTop').onclick=function(){window.scrollTo({top:0,behavior:'smooth'})};
  document.getElementById('btnReload').onclick=function(){try{frame(active).contentWindow.location.reload()}catch(e){}};
  document.getElementById('btnPrint').onclick=function(){try{frame(active).contentWindow.focus();frame(active).contentWindow.print()}catch(e){}};
  document.getElementById('btnOpen').onclick=function(){window.open(MAP[active].url,'_blank','noopener')};

  // 兼容旧链接：index.html#clients 等 -> 总览看板并滚动到对应章节
  var legacy=/^#([a-zA-Z][\w-]*)$/.exec(location.hash);
  var start=/^#\/([a-z]+)/.exec(location.hash);
  show(start?start[1]:'analysis',false);
  if(legacy){
    var t=setInterval(function(){
      if(loaded.analysis && frame('analysis').contentDocument){
        clearInterval(t);setTimeout(function(){scrollAnchor(legacy[1]);markChip(legacy[1])},350);
      }
    },200);
    setTimeout(function(){clearInterval(t)},8000);
  }

  // 自检：?selftest=1 时依次加载 4 个 Tab 并把结果写入 DOM，供 headless 验证
  if(/[?&]selftest=1/.test(location.search)){
    var order=Object.keys(MAP),i=0,res=[];
    function step(){
      if(i>=order.length){
        var pre=document.createElement('pre');pre.id='selftest';
        pre.setAttribute('data-result','ok');pre.textContent=JSON.stringify(res);
        document.body.appendChild(pre);return;
      }
      var k=order[i++];show(k,false);
      var n=0,poll=setInterval(function(){
        n++;
        var f=frame(k),h=fit(k),title='',h1='';
        try{var d=f.contentDocument;title=d.title;h1=d.querySelector('h1')?d.querySelector('h1').textContent.trim().slice(0,40):''}catch(e){}
        if((h>500&&title)||n>40){
          clearInterval(poll);
          buildChips(k);
          res.push({key:k,height:h,title:title.slice(0,50),h1:h1,
                    chips:document.querySelectorAll('#chips .chip').length,
                    embedded:(function(){try{return f.contentDocument.documentElement.classList.contains('embedded')}catch(e){return false}})()});
          step();
        }
      },250);
    }
    setTimeout(step,600);
  }

  // 自检 2：验证「子页互链接管 / 章节跳转 / 计算器在 Tab 内可算」
  if(/[?&]selftest=2/.test(location.search)){
    var out2={};
    function waitFrame(k,cb){
      var n=0,p=setInterval(function(){
        n++;
        try{var d=frame(k).contentDocument;
          if(d&&d.body&&d.body.scrollHeight>500){clearInterval(p);cb(d);return}
        }catch(e){}
        if(n>60){clearInterval(p);cb(null)}
      },200);
    }
    setTimeout(function(){
      waitFrame('analysis',function(d){
        var a=d&&d.querySelector('a[href="segments.html"]');
        out2.linkFound=!!a;
        if(a) a.dispatchEvent(new d.defaultView.MouseEvent('click',{bubbles:true,cancelable:true}));
        setTimeout(function(){
          out2.activeAfterLink=active;
          var chip=document.querySelectorAll('#chips .chip')[3];
          if(chip){out2.chip=chip.textContent;chip.click()}
          setTimeout(function(){
            out2.scrollY=window.scrollY;
            out2.calcY=window.__lastScrollY;
            out2.docH=document.documentElement.scrollHeight;
            out2.innerH=window.innerHeight;
            show('quotation',false);
            waitFrame('quotation',function(q){
              out2.kpi=q&&q.getElementById('kpis')?q.getElementById('kpis').textContent.replace(/\s+/g,' ').slice(0,150):'none';
              out2.quoteCn=q&&q.getElementById('quoteCn')?q.getElementById('quoteCn').textContent.slice(0,60):'none';
              var pre=document.createElement('pre');pre.id='selftest2';
              pre.textContent=JSON.stringify(out2);document.body.appendChild(pre);
            });
          },900);
        },500);
      });
    },900);
  }
})();
</script>
</body></html>
'''


def build():
    # 1) 原看板另存 analysis.html；若 index.html 已是 Tab 容器，则复用已生成的看板，
    #    找不到时再从固定的基线提交 153d69c 取回，保证脚本可反复运行。
    cur = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    ana = os.path.join(ROOT, 'analysis.html')
    if 'id="ru-tab-shell"' in cur:
        if not (os.path.exists(ana) and os.path.getsize(ana) > 100000
                and 'id="ru-tab-shell"' not in open(ana, encoding='utf-8').read()):
            tmp = os.path.join(ROOT, 'tools', '.orig_index.html')
            raw = subprocess.check_output(
                ['git', '-C', ROOT, 'show', '153d69c:index.html'])
            open(tmp, 'w', encoding='utf-8').write(raw.decode('utf-8'))
            patch_child(os.path.join('tools', '.orig_index.html'), 'analysis.html')
            os.remove(tmp)
        else:
            patch_child('analysis.html', 'analysis.html')
    else:
        patch_child('index.html', 'analysis.html')
    # 2) 其余三页原地改写
    for f in ('segments.html', 'quotation.html', 'rules.html'):
        patch_child(f, f)
    # 3) 生成 Tab 容器
    shell = (SHELL
             .replace('__TAB_BUTTONS__', TAB_BUTTONS)
             .replace('__FRAMES__', FRAMES)
             .replace('__FOOTER_LINKS__', FOOTER_LINKS)
             .replace('__TABMAP__', json.dumps(
                 {t['key']: {'name': t['name'], 'url': t['url']} for t in TABS},
                 ensure_ascii=False)))
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(shell)
    for f in ('index.html', 'analysis.html', 'segments.html', 'quotation.html', 'rules.html'):
        print('%-18s %8d bytes' % (f, os.path.getsize(os.path.join(ROOT, f))))


if __name__ == '__main__':
    build()
