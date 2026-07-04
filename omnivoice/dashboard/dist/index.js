/*
 * OmniVoice — dashboard Voices tab.
 *
 * Plain IIFE against window.__HERMES_PLUGIN_SDK__ (no bundled React). Registers
 * a single tab component. Calls send the dashboard session token as a bearer so
 * they work on hardened Hermes builds that gate plugin API routes.
 */
(function () {
  "use strict";

  var SDK = window.__HERMES_PLUGIN_SDK__;
  var React = SDK.React;
  var h = React.createElement;
  var useState = SDK.hooks.useState;
  var useEffect = SDK.hooks.useEffect;
  var useRef = SDK.hooks.useRef;
  var useCallback = SDK.hooks.useCallback;
  var C = SDK.components;

  var BASE = "/api/plugins/omnivoice";
  var TOKEN = window.__HERMES_SESSION_TOKEN__ || "";
  function authHeaders(hh) { hh = hh || {}; if (TOKEN) hh["Authorization"] = "Bearer " + TOKEN; return hh; }

  function api(path, opts) {
    opts = opts || {};
    opts.credentials = "include";
    opts.headers = authHeaders(opts.headers);
    return fetch(BASE + path, opts).then(function (res) {
      if (!res.ok) {
        return res.json().then(
          function (j) { throw new Error(j.detail || ("HTTP " + res.status)); },
          function () { throw new Error("HTTP " + res.status); }
        );
      }
      return res.json();
    });
  }
  function jsonReq(path, body, method) {
    return api(path, { method: method || "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  }

  // ---- helpers ---------------------------------------------------------

  function Field(props) { return h("div", { className: "ov-field" }, h(C.Label, null, props.label), props.children); }
  function Notice(props) { if (!props.text) return null; return h("div", { className: "ov-notice ov-notice-" + (props.kind || "error") }, props.text); }

  function splitItems(s) { return (s || "").split(/[,，]/).map(function (x) { return x.trim(); }).filter(Boolean); }
  function addTerm(instruct, term) { var items = splitItems(instruct); if (items.indexOf(term) === -1) items.push(term); return items.join(", "); }
  function badTerms(instruct, vocab) {
    if (!vocab) return [];
    var valid = {};
    Object.keys(vocab).forEach(function (c) { vocab[c].forEach(function (t) { valid[t.toLowerCase()] = true; }); });
    return splitItems(instruct).filter(function (t) { return !valid[t.toLowerCase()]; });
  }

  // Clickable guide of the valid instruct attributes; clicking one appends it.
  function TermGuide(props) {
    if (!props.vocab) return null;
    return h("div", { className: "ov-vocab" },
      h("div", { className: "ov-vocab-title" }, "Supported attributes (click to add):"),
      Object.keys(props.vocab).map(function (cat) {
        return h("div", { className: "ov-vocab-row", key: cat },
          h("span", { className: "ov-vocab-cat" }, cat),
          props.vocab[cat].map(function (term) {
            return h(C.Badge, { key: term, className: "ov-term", onClick: function () { props.onPick(term); } }, term);
          })
        );
      })
    );
  }

  // ---- voice grid ------------------------------------------------------

  function VoiceCard(props) {
    var v = props.voice;
    var busy = props.busyId === v.id;
    return h(C.Card, { className: "ov-card" + (v.active ? " ov-card-active" : "") },
      h(C.CardHeader, null,
        h("div", { className: "ov-card-head" },
          h(C.CardTitle, null, v.name),
          h(C.Badge, null, v.mode),
          v.active ? h(C.Badge, { className: "ov-active-badge" }, "active") : null
        )
      ),
      h(C.CardContent, null,
        h("div", { className: "ov-meta" },
          h("span", null, "lang: " + (v.language || "en")),
          v.mode === "design" && v.instruct ? h("span", { className: "ov-instruct" }, "“" + v.instruct + "”") : null
        ),
        h("div", { className: "ov-row" },
          h(C.Button, { disabled: busy || v.active, onClick: function () { props.onActivate(v.id); } }, v.active ? "Selected" : "Set active"),
          h(C.Button, { variant: "secondary", disabled: busy, onClick: function () { props.onPreview(v.id); } }, busy ? "…" : "Preview"),
          h(C.Button, { variant: "secondary", disabled: busy, onClick: function () { props.onEdit(v); } }, "Edit"),
          h(C.Button, { variant: "destructive", disabled: busy, onClick: function () { props.onDelete(v.id); } }, "Delete")
        )
      )
    );
  }

  function VoiceGrid(props) {
    if (!props.voices.length) return h("p", { className: "ov-empty" }, "No voices yet. Clone one from a reference sample or design one from a prompt.");
    return h("div", { className: "ov-grid" },
      props.voices.map(function (v) {
        return h(VoiceCard, { key: v.id, voice: v, busyId: props.busyId, onActivate: props.onActivate, onPreview: props.onPreview, onDelete: props.onDelete, onEdit: props.onEdit });
      })
    );
  }

  // ---- clone form ------------------------------------------------------

  function CloneForm(props) {
    var s = useState({ id: "", name: "", ref_text: "", language: "en", uses: "personal_assistant,local_generation", consent: false });
    var form = s[0], setForm = s[1];
    var fileRef = useRef(null);
    var upd = function (k) { return function (e) { var val = e && e.target ? (e.target.type === "checkbox" ? e.target.checked : e.target.value) : e; setForm(Object.assign({}, form, { [k]: val })); }; };

    var submit = function () {
      var file = fileRef.current && fileRef.current.files ? fileRef.current.files[0] : null;
      if (!file) { props.onError("Choose a WAV reference sample first."); return; }
      if (!form.consent) { props.onError("Confirm consent to create a clone."); return; }
      var fd = new FormData();
      fd.append("ref_audio", file);
      fd.append("id", form.id);
      fd.append("name", form.name);
      fd.append("ref_text", form.ref_text);
      fd.append("language", form.language);
      fd.append("allowed_uses", form.uses);
      fd.append("consent_source", "user_uploaded");
      fd.append("consent_confirmed", form.consent ? "true" : "false");
      props.onSubmit(api("/voices/clone", { method: "POST", body: fd }));
    };

    return h(C.Card, { className: "ov-form-card" },
      h(C.CardHeader, null, h(C.CardTitle, null, "Clone a voice")),
      h(C.CardContent, null,
        h(Field, { label: "Voice id (a-z0-9-_)" }, h(C.Input, { value: form.id, onChange: upd("id"), placeholder: "marvin" })),
        h(Field, { label: "Display name" }, h(C.Input, { value: form.name, onChange: upd("name"), placeholder: "Marvin" })),
        h(Field, { label: "Reference sample (.wav)" }, h("input", { type: "file", accept: "audio/wav,.wav", ref: fileRef, className: "ov-file" })),
        h("p", { className: "ov-hint" }, "Use a short, clean clip (~10–30s). Long references are rejected — they degrade quality and can exhaust GPU memory."),
        h(Field, { label: "Reference transcript (exact words spoken in the sample)" },
          h("textarea", { className: "ov-textarea", value: form.ref_text, onChange: upd("ref_text"), rows: 3 })),
        h(Field, { label: "Language" }, h(C.Input, { value: form.language, onChange: upd("language") })),
        h(Field, { label: "Allowed uses (comma separated)" }, h(C.Input, { value: form.uses, onChange: upd("uses") })),
        h("label", { className: "ov-consent" },
          h("input", { type: "checkbox", checked: form.consent, onChange: upd("consent") }),
          h("span", null, "I have the right to clone this voice and consent to its use.")),
        h(C.Button, { onClick: submit, disabled: props.busy }, props.busy ? "Cloning…" : "Create clone")
      )
    );
  }

  // ---- design form -----------------------------------------------------

  function DesignForm(props) {
    var s = useState({ id: "", name: "", instruct: "", language: "en", consent: false });
    var form = s[0], setForm = s[1];
    var upd = function (k) { return function (e) { var val = e && e.target ? (e.target.type === "checkbox" ? e.target.checked : e.target.value) : e; setForm(Object.assign({}, form, { [k]: val })); }; };
    var pick = function (term) { setForm(Object.assign({}, form, { instruct: addTerm(form.instruct, term) })); };

    var submit = function () {
      if (!form.consent) { props.onError("Confirm consent to create a voice."); return; }
      var bad = badTerms(form.instruct, props.vocab);
      if (bad.length) { props.onError("Unsupported attribute(s): " + bad.join(", ") + ". Use only the attributes below."); return; }
      props.onSubmit(jsonReq("/voices/design", { id: form.id, name: form.name, instruct: form.instruct, language: form.language, consent_source: "user_created" }));
    };

    return h(C.Card, { className: "ov-form-card" },
      h(C.CardHeader, null, h(C.CardTitle, null, "Design a voice")),
      h(C.CardContent, null,
        h(Field, { label: "Voice id (a-z0-9-_)" }, h(C.Input, { value: form.id, onChange: upd("id"), placeholder: "narrator" })),
        h(Field, { label: "Display name" }, h(C.Input, { value: form.name, onChange: upd("name"), placeholder: "Narrator" })),
        h(Field, { label: "Instruction (attributes, comma-separated)" },
          h("textarea", { className: "ov-textarea", value: form.instruct, onChange: upd("instruct"), rows: 2, placeholder: "male, american accent, moderate pitch" })),
        h(TermGuide, { vocab: props.vocab, onPick: pick }),
        h(Field, { label: "Language" }, h(C.Input, { value: form.language, onChange: upd("language") })),
        h("label", { className: "ov-consent" },
          h("input", { type: "checkbox", checked: form.consent, onChange: upd("consent") }),
          h("span", null, "I consent to creating and using this synthetic voice.")),
        h(C.Button, { onClick: submit, disabled: props.busy }, props.busy ? "Creating…" : "Create voice")
      )
    );
  }

  // ---- edit form -------------------------------------------------------

  function EditForm(props) {
    var v = props.voice;
    var s = useState({ name: v.name || "", language: v.language || "en", instruct: v.instruct || "", ref_text: "" });
    var form = s[0], setForm = s[1];
    var upd = function (k) { return function (e) { var val = e && e.target ? e.target.value : e; setForm(Object.assign({}, form, { [k]: val })); }; };
    var pick = function (term) { setForm(Object.assign({}, form, { instruct: addTerm(form.instruct, term) })); };

    var save = function () {
      var patch = { name: form.name, language: form.language };
      if (v.mode === "design") {
        var bad = badTerms(form.instruct, props.vocab);
        if (bad.length) { props.onError("Unsupported attribute(s): " + bad.join(", ") + "."); return; }
        patch.instruct = form.instruct;
      } else if (form.ref_text.trim()) {
        patch.ref_text = form.ref_text.trim();
      }
      props.onSave(v.id, patch);
    };

    return h(C.Card, { className: "ov-form-card ov-edit-card" },
      h(C.CardHeader, null, h("div", { className: "ov-card-head" }, h(C.CardTitle, null, "Edit “" + v.name + "”"), h(C.Badge, null, v.mode))),
      h(C.CardContent, null,
        h(Field, { label: "Display name" }, h(C.Input, { value: form.name, onChange: upd("name") })),
        h(Field, { label: "Language" }, h(C.Input, { value: form.language, onChange: upd("language") })),
        v.mode === "design"
          ? h("div", null,
              h(Field, { label: "Instruction (attributes, comma-separated)" },
                h("textarea", { className: "ov-textarea", value: form.instruct, onChange: upd("instruct"), rows: 2 })),
              h(TermGuide, { vocab: props.vocab, onPick: pick }))
          : h("div", null,
              h(Field, { label: "Reference transcript (blank = keep current)" },
                h("textarea", { className: "ov-textarea", value: form.ref_text, onChange: upd("ref_text"), rows: 3 })),
              h("p", { className: "ov-hint" }, "The reference audio can't be changed here — delete and re-clone to replace it.")),
        h("div", { className: "ov-row" },
          h(C.Button, { onClick: save, disabled: props.busy }, props.busy ? "Saving…" : "Save changes"),
          h(C.Button, { variant: "secondary", onClick: props.onCancel, disabled: props.busy }, "Cancel"))
      )
    );
  }

  // ---- talk tab --------------------------------------------------------
  //
  // A browser voice conversation with the Hermes agent. Each turn: record the
  // mic → native /api/audio/transcribe (STT) → plugin /talk (the agent, via
  // `hermes chat -q -Q --resume`) → speak the reply through the active
  // OmniVoice voice (/voices/{id}/preview). Conversation state lives on the
  // page so it survives tab switches; updates are functional to stay correct
  // across the async record→think→speak chain.

  function nativeTranscribe(dataUrl, mime) {
    return fetch("/api/audio/transcribe", {
      method: "POST", credentials: "include",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ data_url: dataUrl, mime_type: mime }),
    }).then(function (res) {
      if (!res.ok) { return res.json().then(function (j) { throw new Error(j.detail || ("HTTP " + res.status)); }); }
      return res.json();
    });
  }

  function Bubble(props) {
    var m = props.msg;
    return h("div", { className: "ov-msg ov-msg-" + m.role + (m.error ? " ov-msg-error" : "") },
      h("div", { className: "ov-msg-who" }, m.role === "user" ? "You" : "Agent"),
      h("div", { className: "ov-msg-text" }, m.text)
    );
  }

  function TalkTab(props) {
    var t = props.state;                 // { msgs, session, status, input }
    var setTalk = props.setState;
    var mrRef = useRef(null);
    var chunksRef = useRef([]);
    var audioRef = props.audioRef;       // shared page player, so replies are replayable
    var scrollRef = useRef(null);

    var busy = t.status && t.status !== "recording"; // transcribing | thinking | speaking
    var recording = t.status === "recording";

    var patch = function (o) { setTalk(function (p) { return Object.assign({}, p, o); }); };
    var appendMsg = function (m) { setTalk(function (p) { return Object.assign({}, p, { msgs: p.msgs.concat([m]) }); }); };
    var setStatus = function (s) { setTalk(function (p) { return Object.assign({}, p, { status: s }); }); };

    useEffect(function () {
      if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }, [t.msgs.length, t.status]);

    var speak = function (text) {
      if (!props.activeVoice) { setStatus(""); return; }
      setStatus("speaking");
      return fetch(BASE + "/voices/" + props.activeVoice + "/preview", {
        method: "POST", credentials: "include",
        headers: authHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({ text: text }),
      }).then(function (res) {
        if (!res.ok) { return res.json().then(function (j) { throw new Error(j.detail || ("HTTP " + res.status)); }); }
        return res.blob();
      }).then(function (blob) {
        var url = URL.createObjectURL(blob);
        if (audioRef.current) { audioRef.current.src = url; return audioRef.current.play(); }
      }).catch(function (e) {
        props.onError("Reply received, but couldn't speak it: " + e.message);
      }).then(function () { setStatus(""); });
    };

    var sendText = function (raw) {
      var text = (raw || "").trim();
      if (!text || busy) return;
      var sess = t.session;
      props.onError("");
      appendMsg({ role: "user", text: text });
      patch({ input: "", status: "thinking" });
      jsonReq("/talk", { text: text, session_id: sess })
        .then(function (r) {
          setTalk(function (p) { return Object.assign({}, p, { session: r.session_id || p.session, msgs: p.msgs.concat([{ role: "assistant", text: r.reply }]) }); });
          return speak(r.reply);
        })
        .catch(function (e) {
          appendMsg({ role: "assistant", text: "⚠️ " + e.message, error: true });
          setStatus("");
        });
    };

    var transcribeAndSend = function (blob) {
      setStatus("transcribing");
      var reader = new FileReader();
      reader.onloadend = function () {
        nativeTranscribe(reader.result, blob.type || "audio/webm")
          .then(function (j) {
            var text = ((j && j.transcript) || "").trim();
            if (!text) { setStatus(""); props.onError("Didn't catch that — try again, or type instead."); return; }
            sendText(text);
          })
          .catch(function (e) { setStatus(""); props.onError("Transcription failed: " + e.message); });
      };
      reader.readAsDataURL(blob);
    };

    var startRec = function () {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) { props.onError("This browser can't record audio."); return; }
      props.onError("");
      navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
        var mr = new MediaRecorder(stream);
        chunksRef.current = [];
        mr.ondataavailable = function (e) { if (e.data && e.data.size) chunksRef.current.push(e.data); };
        mr.onstop = function () {
          stream.getTracks().forEach(function (tr) { tr.stop(); });
          transcribeAndSend(new Blob(chunksRef.current, { type: mr.mimeType || "audio/webm" }));
        };
        mrRef.current = mr;
        mr.start();
        setStatus("recording");
      }).catch(function (e) { props.onError("Microphone unavailable: " + e.message); });
    };

    var stopRec = function () { if (mrRef.current && mrRef.current.state !== "inactive") mrRef.current.stop(); };

    var statusLabel = { recording: "🎙️ Recording… tap Stop when done", transcribing: "✍️ Transcribing…", thinking: "🧠 Agent is thinking…", speaking: "🔊 Speaking…" };

    return h("div", { className: "ov-talk" },
      h("p", { className: "ov-hint" },
        props.activeVoice
          ? "Voice chat with your Hermes agent — it replies out loud in your active voice (“" + props.activeVoice + "”). This drives the real agent (tools included); each turn takes a few seconds."
          : "Set an active voice in the Voices tab to hear spoken replies. You can still chat by text below."),
      h("div", { className: "ov-transcript", ref: scrollRef },
        t.msgs.length
          ? t.msgs.map(function (m, i) { return h(Bubble, { key: i, msg: m }); })
          : h("p", { className: "ov-empty" }, "Say something, or type below, to start talking with your agent.")
      ),
      t.status ? h("div", { className: "ov-status-pill" }, statusLabel[t.status] || t.status) : null,
      h("div", { className: "ov-talk-input" },
        h(C.Button, {
          className: "ov-mic" + (recording ? " ov-mic-on" : ""),
          variant: recording ? "destructive" : "secondary",
          disabled: busy,
          onClick: recording ? stopRec : startRec,
        }, recording ? "⏹ Stop" : "🎙️ Record"),
        h("input", {
          className: "ov-input ov-talk-text",
          value: t.input,
          placeholder: busy ? "…" : "Type a message and press Enter",
          disabled: busy || recording,
          onChange: function (e) { patch({ input: e.target.value }); },
          onKeyDown: function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendText(t.input); } },
        }),
        h(C.Button, { disabled: busy || recording || !t.input.trim(), onClick: function () { sendText(t.input); } }, "Send")
      )
    );
  }

  // ---- page ------------------------------------------------------------

  function VoicesPage() {
    var vs = useState({ voices: [], active: null, backend: "" }); var state = vs[0], setState = vs[1];
    var es = useState(""); var err = es[0], setErr = es[1];
    var ns = useState(""); var note = ns[0], setNote = ns[1];
    var bs = useState(null); var busyId = bs[0], setBusyId = bs[1];
    var fbs = useState(false); var formBusy = fbs[0], setFormBusy = fbs[1];
    var ts = useState("voices"); var tab = ts[0], setTab = ts[1];
    var vv = useState(null); var vocab = vv[0], setVocab = vv[1];
    var eds = useState(null); var editing = eds[0], setEditing = eds[1];
    var tk = useState({ msgs: [], session: "", status: "", input: "" }); var talk = tk[0], setTalk = tk[1];
    var audioRef = useRef(null);

    var refresh = useCallback(function () { return api("/voices", {}).then(setState).catch(function (e) { setErr(e.message); }); }, []);
    useEffect(function () {
      refresh();
      api("/instruct-vocab", {}).then(function (r) { setVocab(r.vocab); }).catch(function () {});
    }, [refresh]);

    var activate = function (id) {
      setBusyId(id); setErr(""); setNote("");
      jsonReq("/voices/" + id + "/active", { set_provider: false }, "PUT")
        .then(function () { setNote("Active voice set to '" + id + "'."); return refresh(); })
        .catch(function (e) { setErr(e.message); })
        .then(function () { setBusyId(null); });
    };

    var remove = function (id) {
      setBusyId(id); setErr(""); setNote("");
      api("/voices/" + id, { method: "DELETE" })
        .then(function () { return refresh(); })
        .catch(function (e) { setErr(e.message); })
        .then(function () { setBusyId(null); });
    };

    var preview = function (id) {
      setBusyId(id); setErr(""); setNote("");
      fetch(BASE + "/voices/" + id + "/preview", {
        method: "POST", credentials: "include",
        headers: authHeaders({ "Content-Type": "application/json" }), body: "{}",
      }).then(function (res) {
        if (!res.ok) { return res.json().then(function (j) { throw new Error(j.detail || ("HTTP " + res.status)); }); }
        return res.blob();
      }).then(function (blob) {
        var url = URL.createObjectURL(blob);
        if (audioRef.current) { audioRef.current.src = url; audioRef.current.play(); }
      }).catch(function (e) { setErr(e.message); })
        .then(function () { setBusyId(null); });
    };

    var onFormSubmit = function (promise) {
      setFormBusy(true); setErr(""); setNote("");
      promise.then(function (r) {
        setNote("Voice '" + (r.voice ? r.voice.id : "") + "' created.");
        return refresh();
      }).catch(function (e) { setErr(e.message); })
        .then(function () { setFormBusy(false); });
    };

    var saveEdit = function (id, patch) {
      setFormBusy(true); setErr(""); setNote("");
      jsonReq("/voices/" + id, patch, "PATCH")
        .then(function () { setNote("Voice '" + id + "' updated."); setEditing(null); return refresh(); })
        .catch(function (e) { setErr(e.message); })
        .then(function () { setFormBusy(false); });
    };

    var startEdit = function (v) { setErr(""); setNote(""); setEditing(v); };

    return h("div", { className: "ov-page" },
      h(C.Card, { className: "ov-status" },
        h(C.CardContent, null,
          h("div", { className: "ov-status-row" },
            h("span", null, "Backend: ", h(C.Badge, null, state.backend || "?")),
            h("span", null, "Active: ", state.active ? h(C.Badge, null, state.active) : h("em", null, "none"))
          )
        )
      ),
      h(Notice, { kind: "error", text: err }),
      h(Notice, { kind: "ok", text: note }),
      editing
        ? h(EditForm, { key: editing.id, voice: editing, vocab: vocab, busy: formBusy, onSave: saveEdit, onCancel: function () { setEditing(null); }, onError: setErr })
        : h("div", null,
            h("div", { className: "ov-tabbar" },
              ["voices", "clone", "design", "talk"].map(function (t) {
                return h(C.Button, {
                  key: t,
                  variant: tab === t ? "default" : "secondary",
                  className: "ov-tabbtn" + (tab === t ? " ov-tabbtn-on" : ""),
                  onClick: function () { setTab(t); },
                }, t.charAt(0).toUpperCase() + t.slice(1));
              })
            ),
            tab === "voices" ? h(VoiceGrid, { voices: state.voices, busyId: busyId, onActivate: activate, onPreview: preview, onDelete: remove, onEdit: startEdit }) : null,
            tab === "clone" ? h(CloneForm, { busy: formBusy, onSubmit: onFormSubmit, onError: setErr }) : null,
            tab === "design" ? h(DesignForm, { busy: formBusy, vocab: vocab, onSubmit: onFormSubmit, onError: setErr }) : null,
            tab === "talk" ? h(TalkTab, { state: talk, setState: setTalk, activeVoice: state.active, audioRef: audioRef, onError: setErr }) : null
          ),
      h("audio", { ref: audioRef, controls: true, className: "ov-audio" })
    );
  }

  window.__HERMES_PLUGINS__.register("omnivoice", VoicesPage);
})();
