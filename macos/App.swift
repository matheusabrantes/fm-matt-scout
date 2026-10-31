import AppKit
import WebKit
import UniformTypeIdentifiers

final class AppDelegate: NSObject, NSApplicationDelegate, WKScriptMessageHandler, WKNavigationDelegate, WKUIDelegate {
    var window: NSWindow!
    var web: WKWebView!
    var process: Process?
    var didLoad = false
    var quitting = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.applicationIconImage = NSWorkspace.shared.icon(forFile: Bundle.main.bundlePath)
        let appMenu = NSMenu()
        let root = NSMenuItem()
        appMenu.addItem(root)
        let menu = NSMenu()
        menu.addItem(withTitle: "About FM Matt Scout", action: #selector(about), keyEquivalent: "")
        menu.addItem(.separator())
        menu.addItem(withTitle: "Quit FM Matt Scout", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")
        root.submenu = menu
        let file = NSMenuItem(title: "File", action: nil, keyEquivalent: "")
        let fileMenu = NSMenu(title: "File")
        fileMenu.addItem(withTitle: "Open Save…", action: #selector(openSave), keyEquivalent: "o")
        file.submenu = fileMenu
        appMenu.addItem(file)
        let edit = NSMenuItem(title: "Edit", action: nil, keyEquivalent: "")
        let editMenu = NSMenu(title: "Edit")
        editMenu.addItem(withTitle: "Copy", action: #selector(NSText.copy(_:)), keyEquivalent: "c")
        editMenu.addItem(withTitle: "Paste", action: #selector(NSText.paste(_:)), keyEquivalent: "v")
        editMenu.addItem(withTitle: "Select All", action: #selector(NSText.selectAll(_:)), keyEquivalent: "a")
        edit.submenu = editMenu
        appMenu.addItem(edit)
        NSApp.mainMenu = appMenu
        let controller = WKUserContentController()
        controller.add(self, name: "openSave")
        controller.add(self, name: "saveFile")
        controller.add(self, name: "copyName")
        controller.add(self, name: "themePreference")
        if let theme = UserDefaults.standard.string(forKey: "fmscout.theme"), ["light", "dark"].contains(theme) {
            NSApp.appearance = NSAppearance(named: theme == "dark" ? .darkAqua : .aqua)
            let seed = "if(location.hostname==='127.0.0.1')window.fmscoutNativeTheme='\(theme)';"
            controller.addUserScript(WKUserScript(source: seed, injectionTime: .atDocumentStart, forMainFrameOnly: true))
        }
        let config = WKWebViewConfiguration()
        config.userContentController = controller
        web = WKWebView(frame: .zero, configuration: config)
        web.navigationDelegate = self
        web.uiDelegate = self
        window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 1400, height: 900), styleMask: [.titled, .closable, .miniaturizable, .resizable], backing: .buffered, defer: false)
        window.title = "FM Matt Scout 26"
        window.minSize = NSSize(width: 850, height: 600)
        window.contentView = web
        window.center()
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        startBackend()
    }

    func startBackend() {
        guard let python = Bundle.main.object(forInfoDictionaryKey: "MattScoutPython") as? String,
              let resources = Bundle.main.resourceURL else { fail("Configuração do aplicativo ausente."); return }
        let p = Process()
        p.executableURL = URL(fileURLWithPath: python)
        p.arguments = [resources.appendingPathComponent("server.py").path]
        p.environment = ProcessInfo.processInfo.environment.merging(["PYTHONDONTWRITEBYTECODE": "1"]) { _, value in value }
        let pipe = Pipe()
        p.standardOutput = pipe
        p.standardError = Pipe()
        pipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard let text = String(data: data, encoding: .utf8),
                  let first = text.split(separator: "\n").first,
                  let url = URL(string: String(first)), url.host == "127.0.0.1" else { return }
            DispatchQueue.main.async {
                guard let self, !self.didLoad else { return }
                self.didLoad = true
                self.web.load(URLRequest(url: url))
                handle.readabilityHandler = nil
            }
        }
        p.terminationHandler = { [weak self] process in
            DispatchQueue.main.async {
                if let self, !self.quitting { self.fail("O leitor local encerrou (código \(process.terminationStatus)). Execute build.command para reconstruir o aplicativo.") }
            }
        }
        do { try p.run(); process = p }
        catch { fail("Não foi possível iniciar Python: \(error.localizedDescription)") }
    }

    func fail(_ message: String) {
        let alert = NSAlert()
        alert.messageText = "FM Matt Scout"
        alert.informativeText = message
        alert.runModal()
    }

    @objc func about() {
        let alert = NSAlert()
        alert.messageText = "FM Matt Scout 26"
        alert.informativeText = "Scouting local de saves do FM26. Somente leitura. Leitor fmsave (MIT). Aplicativo independente, sem vínculo com Sports Interactive, SEGA ou Genie Scout."
        alert.runModal()
    }

    @objc func openSave() {
        guard didLoad else { return }
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [UTType(filenameExtension: "fm") ?? .data]
        panel.canChooseDirectories = false
        panel.allowsMultipleSelection = false
        panel.message = "Selecione um save do Football Manager 26. O arquivo será apenas lido."
        panel.directoryURL = FileManager.default.homeDirectoryForCurrentUser.appendingPathComponent("Library/Application Support/Sports Interactive/Football Manager 26/games")
        panel.beginSheetModal(for: window) { [weak self] response in
            guard response == .OK, let path = panel.url?.path,
                  let data = try? JSONSerialization.data(withJSONObject: path, options: .fragmentsAllowed),
                  let encoded = String(data: data, encoding: .utf8) else { return }
            self?.web.evaluateJavaScript("window.loadSave(\(encoded))")
        }
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard message.frameInfo.isMainFrame, message.frameInfo.securityOrigin.host == "127.0.0.1" else { return }
        if message.name == "openSave" { openSave(); return }
        if message.name == "themePreference", message.frameInfo.request.url?.port == web.url?.port,
           let theme = message.body as? String, ["light", "dark"].contains(theme) {
            UserDefaults.standard.set(theme, forKey: "fmscout.theme")
            NSApp.appearance = NSAppearance(named: theme == "dark" ? .darkAqua : .aqua)
            return
        }
        if message.name == "copyName", message.frameInfo.request.url?.port == web.url?.port,
           let name = message.body as? String, !name.isEmpty, name.utf8.count <= 1024 {
            NSPasteboard.general.clearContents()
            NSPasteboard.general.setString(name, forType: .string)
            return
        }
        if message.name == "saveFile", let body = message.body as? [String: String],
           let filename = body["filename"], let contents = body["contents"] {
            let panel = NSSavePanel()
            panel.nameFieldStringValue = URL(fileURLWithPath: filename).lastPathComponent
            panel.allowedContentTypes = [UTType(filenameExtension: URL(fileURLWithPath: filename).pathExtension) ?? .data]
            panel.allowsOtherFileTypes = false
            panel.canCreateDirectories = true
            panel.beginSheetModal(for: window) { [weak self] response in
                guard response == .OK, let url = panel.url else { return }
                guard ["csv", "json"].contains(url.pathExtension.lowercased()) else {
                    self?.fail("Escolha um arquivo CSV ou JSON. Saves .fm não podem ser sobrescritos.")
                    return
                }
                do { try contents.write(to: url, atomically: true, encoding: .utf8) }
                catch { self?.fail("Não foi possível salvar: \(error.localizedDescription)") }
            }
        }
    }

    func webView(_ webView: WKWebView, runOpenPanelWith parameters: WKOpenPanelParameters, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping ([URL]?) -> Void) {
        let panel = NSOpenPanel()
        panel.allowedContentTypes = [.json]
        panel.allowsMultipleSelection = false
        panel.beginSheetModal(for: window) { response in completionHandler(response == .OK ? panel.urls : nil) }
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else { decisionHandler(.cancel); return }
        decisionHandler(url.host == "127.0.0.1" && (webView.url == nil || url.port == webView.url?.port) ? .allow : .cancel)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool { true }
    func applicationWillTerminate(_ notification: Notification) {
        quitting = true
        if process?.isRunning == true { process?.terminate() }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
