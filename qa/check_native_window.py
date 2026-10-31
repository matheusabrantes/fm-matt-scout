#!/usr/bin/env python3
"""Check the macOS window, WebKit hit testing, and bridge against the real app classes.

Run on macOS with Command Line Tools: python3 qa/check_native_window.py
The local fixture excludes backend/data scripts; all temporary build files are isolated.
"""
from pathlib import Path
import http.server, threading, re, subprocess, hashlib, tempfile

with tempfile.TemporaryDirectory(prefix="fm-native-window-") as scratch:
    root=Path(__file__).resolve().parents[1]
    if not (root/'macos/App.swift').is_file(): root=Path.cwd()
    work=Path(scratch)
    class Handler(http.server.SimpleHTTPRequestHandler):
     def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(root/'web'),**kwargs)
     def log_message(self,*args): pass
     def do_GET(self):
      if self.path=='/':
       data=(root/'web/index.html').read_text()
       data=re.sub(r'<script\b[^>]*>.*?</script>','',data,flags=re.S)
       self.send_response(200); self.send_header('Content-Type','text/html');self.end_headers();self.wfile.write(data.encode())
      else: super().do_GET()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler)
    port=server.server_port
    threading.Thread(target=server.serve_forever,daemon=True).start()
    source=(root/'macos/App.swift').read_text()
    print('SOURCE_SHA256',hashlib.sha256(source.encode()).hexdigest(),flush=True)
    source=source.split('\nlet app = NSApplication.shared\n')[0]
    a=source.index('    func startBackend() {\n'); b=source.index('    func fail(',a)
    source=source[:a]+f'    func startBackend() {{ web.load(URLRequest(url: URL(string: "http://127.0.0.1:{port}/")!)) }}\n\n'+source[b:]
    source+=r'''
    let app = NSApplication.shared
    let owner = AppDelegate()
    var count = 0
    func check(_ condition: @autoclosure () -> Bool, _ label: String) {
        guard condition() else { print("FAIL",label); fflush(stdout); exit(1) }
        count += 1
    }
    func pump(_ seconds: Double = 0.08) async { try? await Task.sleep(nanoseconds: UInt64(seconds * 1_000_000_000)) }
    func js(_ expression: String) async throws -> Any? { try await owner.web.evaluateJavaScript(expression) }
    func topHit(_ x: CGFloat,_ y: CGFloat) -> NSView? {
        let web = owner.web!
        let local = NSPoint(x:x,y:web.isFlipped ? y : web.bounds.height-y)
        return web.hitTest(web.convert(local,to:web.superview))
    }
    func rectNear(_ a: NSRect?,_ b: NSRect,_ tolerance: CGFloat = 1) -> Bool {
        guard let a else { return false }
        return abs(a.minX-b.minX)<tolerance && abs(a.minY-b.minY)<tolerance && abs(a.width-b.width)<tolerance && abs(a.height-b.height)<tolerance
    }
    func domRect(_ selector: String) async throws -> NSRect {
        let value = try await js("(()=>{let r=document.querySelector('"+selector+"').getBoundingClientRect();return [r.x,r.y,r.width,r.height]})()") as! [Double]
        return NSRect(x:value[0],y:value[1],width:value[2],height:value[3])
    }
    app.setActivationPolicy(.regular)
    owner.applicationDidFinishLaunching(Notification(name: NSApplication.didFinishLaunchingNotification))
    owner.window.title = "FM Scout Temporary Native Review"
    owner.window.orderOut(nil)
    Task { @MainActor in
     do {
      for _ in 0..<200 { if owner.web.titlebarDragRect != nil { break }; await pump(0.05) }
      check(owner.web.titlebarDragRect != nil,"production injected ResizeObserver delivered rectangle")
      check(owner.window.styleMask.contains([.titled,.closable,.miniaturizable,.resizable,.fullSizeContentView]),"native style flags retained")
      check(owner.window.titleVisibility == .hidden && owner.window.titlebarAppearsTransparent,"native title integrated")
      check(owner.window.minSize == NSSize(width:850,height:600),"native minimum window size remains850x600")
      for kind in [NSWindow.ButtonType.closeButton,.miniaturizeButton,.zoomButton] {
       let button=owner.window.standardWindowButton(kind)
       check(button != nil && button!.isEnabled && !button!.isHidden,"native control present and enabled \(kind)")
       let frame=owner.web.convert(button!.bounds,from:button!)
       let topY=owner.web.isFlipped ? frame.midY : owner.web.bounds.height-frame.midY
       check(abs(topY-26)<1,"native control centered in52px header")
      }
      for width: CGFloat in [850,1024,1280,1440,1800] {
       for height: CGFloat in [600,900] {
        owner.window.setFrame(NSRect(x:20,y:20,width:width,height:height),display:false)
        owner.window.layoutIfNeeded(); await pump(0.2)
        check(abs(owner.web.bounds.width-width)<1 && abs(owner.web.bounds.height-height)<1,"fullwindow native web size \(width)x\(height)")
        check(abs(owner.window.frame.height-owner.window.contentLayoutRect.height-52)<1,"native toolbar remains52px under resize")
        for collapsed in [false,true] {
         for actions in [false,true] {
          _=try await js("document.body.classList.toggle('sidebar-collapsed',\(collapsed));document.querySelector('#toolbar-actions').hidden=\(!actions)")
          await pump(0.4)
          let heading=try await domRect(".toolbar-heading")
          let header=try await domRect(".titlebar")
          let expected=NSRect(x:heading.minX,y:0,width:heading.width,height:52)
          check(abs(header.minY)<1 && abs(header.height-52)<1,"web header y0/height52")
          check(rectNear(owner.web.titlebarDragRect,expected),"native bridge tracks heading rectangle")
          check(topHit(heading.midX,26)==nil,"heading falls through to native titlebar")
          let toggle=try await domRect("#sidebar-toggle")
          check(topHit(toggle.midX,toggle.midY) != nil,"sidebar toggle remains web interactive")
          let theme=try await domRect("#theme-toggle")
          check(topHit(theme.midX,theme.midY) != nil,"theme remains web interactive")
          check(topHit(heading.midX,100) != nil,"content below header remains web interactive")
          check(topHit(heading.midX,52) != nil,"drag region stops exactly at header boundary")
          if actions {
           let search=try await domRect("#search")
           check(topHit(search.midX,search.midY) != nil,"search remains web interactive")
           let filters=try await domRect("#advanced-button")
           check(topHit(filters.midX,filters.midY) != nil,"filters remain web interactive")
          }
         }
        }
       }
      }
      print("PASS geometry/hit-testing across 40 width/height/sidebar/action states")
      // Invalid input tests traverse the actual WKScriptMessageHandler via WebKit.
      let invalid = ["null","'wrong'","{}","[]","[10,0,100]","[10,0,100,52,0]","[-1,0,100,52]","[10,1,100,52]","[10,0,-1,52]","[10,0,100,51]","[999999,0,100,52]","[10,0,999999,52]","[NaN,0,100,52]","[10,0,Infinity,52]","['x',0,100,52]"]
      for payload in invalid {
       owner.web.titlebarDragRect=NSRect(x:100,y:0,width:100,height:52)
       _=try await js("(()=>{window.webkit.messageHandlers.windowDragRegion.postMessage(\(payload));return true})()")
       await pump()
       check(owner.web.titlebarDragRect==nil,"invalid bridge geometry rejected: \(payload)")
      }
      for payload in ["[10,0,100,52]","[0,0,0,52]","[0,0,innerWidth,52]"] {
       _=try await js("(()=>{window.webkit.messageHandlers.windowDragRegion.postMessage(\(payload));return true})()")
       await pump();check(owner.web.titlebarDragRect != nil,"valid bridge geometry accepted")
      }
      owner.web.titlebarDragRect=NSRect(x:100,y:0,width:100,height:52)
      _=try await js("(()=>{let f=document.createElement('iframe');f.style.display='none';f.style.position='fixed';f.srcdoc='<script>window.webkit.messageHandlers.windowDragRegion.postMessage([0,0,500,52])<'+ '/script>';document.body.append(f);return true})()")
      await pump(0.3)
      check(owner.web.titlebarDragRect==NSRect(x:100,y:0,width:100,height:52),"subframe bridge rejected")
      let old=owner.web.url
      owner.web.load(URLRequest(url:URL(string:"http://127.0.0.2/")!))
      await pump(0.3);check(owner.web.url==old,"navigation to different host rejected")
      print("PASS invalid geometry, valid boundaries, subframe and foreign-host navigation")

      owner.window.setFrame(NSRect(x:60,y:60,width:1000,height:700),display:false)
      owner.window.makeKeyAndOrderFront(nil)
      await pump(0.3)
      var entered = 0, exited = 0, minimized = 0, restored = 0
      let center = NotificationCenter.default
      let observers = [
        center.addObserver(forName:NSWindow.didEnterFullScreenNotification,object:owner.window,queue:.main){_ in entered += 1},
        center.addObserver(forName:NSWindow.didExitFullScreenNotification,object:owner.window,queue:.main){_ in exited += 1},
        center.addObserver(forName:NSWindow.didMiniaturizeNotification,object:owner.window,queue:.main){_ in minimized += 1},
        center.addObserver(forName:NSWindow.didDeminiaturizeNotification,object:owner.window,queue:.main){_ in restored += 1}
      ]
      print("FULLSCREEN_COLLECTION_BEHAVIOR",owner.window.collectionBehavior.rawValue);fflush(stdout)
      owner.window.toggleFullScreen(nil)
      for _ in 0..<200 { if entered>0 {break};await pump(0.05) }
      check(entered==1 && owner.window.styleMask.contains(.fullScreen),"native fullscreen enter notification and state")
      owner.window.toggleFullScreen(nil)
      for _ in 0..<200 { if exited>0 {break};await pump(0.05) }
      check(exited==1 && !owner.window.styleMask.contains(.fullScreen),"native fullscreen exit notification and state")
      await pump(0.2)
      check(abs(owner.window.frame.height-owner.window.contentLayoutRect.height-52)<1,"native titlebar height restored after fullscreen")
      check(abs(owner.web.bounds.height-owner.window.frame.height)<1,"fullwindow web restored after fullscreen")
      owner.window.performMiniaturize(nil)
      for _ in 0..<100 { if minimized>0 {break};await pump(0.05) }
      check(minimized==1 && owner.window.isMiniaturized,"native minimize notification and state")
      owner.window.deminiaturize(nil)
      for _ in 0..<100 { if restored>0 {break};await pump(0.05) }
      check(restored==1 && !owner.window.isMiniaturized,"native restore notification and state")
      for observer in observers {center.removeObserver(observer)}
      print("PASS native fullscreen enter/exit and minimize/restore notifications")

      print("TOTAL_ASSERTIONS",count)
      print("NATIVE_TITLEBAR_HEIGHT",owner.window.frame.height-owner.window.contentLayoutRect.height)
      fflush(stdout)
      owner.window.orderOut(nil)
      exit(0)
     } catch { print("ERROR",error);fflush(stdout);exit(2) }
    }
    app.run()
    '''
    (work/'main.swift').write_text(source)
    result=subprocess.run(['xcrun','swiftc',str(work/'main.swift'),'-framework','AppKit','-framework','WebKit','-o',str(work/'native-checks')],capture_output=True,text=True)
    print(result.stdout,result.stderr,flush=True)
    if result.returncode: raise SystemExit(result.returncode)
    try:
     result=subprocess.run([str(work/'native-checks')],capture_output=True,text=True,timeout=70)
     print(result.stdout,result.stderr,flush=True)
     raise SystemExit(result.returncode)
    finally: server.shutdown()
