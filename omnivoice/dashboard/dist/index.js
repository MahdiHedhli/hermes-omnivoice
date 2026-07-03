/*
 * OmniVoice — dashboard Voices tab.
 *
 * Plain IIFE against window.__HERMES_PLUGIN_SDK__ (no bundled React). Registers
 * a single tab component. JSON calls go through window.fetch with same-origin
 * credentials; plugin API routes bypass the dashboard auth gate, and the
 * session cookie is sent automatically for the gated case.
 *
 * If you prefer JSX, rebuild this file with esbuild/Vite (React external, IIFE
 * output). The only hard requirement is a single <script>-loadable JS file.
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

  // Hardened Hermes builds (June 2026+) gate plugin API routes behind the
  // dashboard session token, injected into the SPA as
  // window.__HERMES_SESSION_TOKEN__. Older builds bypass plugin-route auth;
  // sending the bearer when it's present works on both. Without this the Voices
  // tab gets 401 on every call ("Unauthorized").
  var TOKEN = window.__HERMES_SESSION_TOKEN__ || "";
  function authHeaders(h) {
    h = h || {};
    if (TOKEN) h["Authorization"] = "Bearer " + TOKEN;
    return h;
  }

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

  function jsonPost(path, body, method) {
    return api(path, {
      method: method || "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    });
  }

  // ---- small presentational helpers ------------------------------------

  function Field(props) {
    return h("div", { className: "ov-field" },
      h(C.Label, null, props.label),
      props.children
    );
  }

  function Notice(props) {
    if (!props.text) return null;
    var kind = props.kind || "error";
    return h("div", { className: "ov-notice ov-notice-" + kind }, props.text);
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
          v.mode === "design" && v.instruct
            ? h("span", { className: "ov-instruct" }, "\u201C" + v.instruct + "\u201D")
            : null
        ),
        h("div", { className: "ov-row" },
          h(C.Button, {
            disabled: busy || v.active,
            onClick: function () { props.onActivate(v.id); },
          }, v.active ? "Selected" : "Set active"),
          h(C.Button, {
            variant: "secondary",
            disabled: busy,
            onClick: function () { props.onPreview(v.id); },
          }, busy ? "\u2026" : "Preview"),
          h(C.Button, {
            variant: "destructive",
            disabled: busy,
            onClick: function () { props.onDelete(v.id); },
          }, "Delete")
        )
      )
    );
  }

  function VoiceGrid(props) {
    if (!props.voices.length) {
      return h("p", { className: "ov-empty" },
        "No voices yet. Clone one from a reference sample or design one from a prompt.");
    }
    return h("div", { className: "ov-grid" },
      props.voices.map(function (v) {
        return h(VoiceCard, {
          key: v.id, voice: v, busyId: props.busyId,
          onActivate: props.onActivate, onPreview: props.onPreview, onDelete: props.onDelete,
        });
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
        h(Field, { label: "Reference transcript (exact words spoken in the sample)" },
          h("textarea", { className: "ov-textarea", value: form.ref_text, onChange: upd("ref_text"), rows: 3 })),
        h(Field, { label: "Language" }, h(C.Input, { value: form.language, onChange: upd("language") })),
        h(Field, { label: "Allowed uses (comma separated)" }, h(C.Input, { value: form.uses, onChange: upd("uses") })),
        h("label", { className: "ov-consent" },
          h("input", { type: "checkbox", checked: form.consent, onChange: upd("consent") }),
          h("span", null, "I have the right to clone this voice and consent to its use.")),
        h(C.Button, { onClick: submit, disabled: props.busy }, props.busy ? "Cloning\u2026" : "Create clone")
      )
    );
  }

  // ---- design form -----------------------------------------------------

  function DesignForm(props) {
    var s = useState({ id: "", name: "", instruct: "", language: "en", consent: false });
    var form = s[0], setForm = s[1];
    var upd = function (k) { return function (e) { var val = e && e.target ? (e.target.type === "checkbox" ? e.target.checked : e.target.value) : e; setForm(Object.assign({}, form, { [k]: val })); }; };

    var submit = function () {
      if (!form.consent) { props.onError("Confirm consent to create a voice."); return; }
      props.onSubmit(jsonPost("/voices/design", {
        id: form.id, name: form.name, instruct: form.instruct, language: form.language,
        consent_source: "user_created",
      }));
    };

    return h(C.Card, { className: "ov-form-card" },
      h(C.CardHeader, null, h(C.CardTitle, null, "Design a voice")),
      h(C.CardContent, null,
        h(Field, { label: "Voice id (a-z0-9-_)" }, h(C.Input, { value: form.id, onChange: upd("id"), placeholder: "narrator" })),
        h(Field, { label: "Display name" }, h(C.Input, { value: form.name, onChange: upd("name"), placeholder: "Narrator" })),
        h(Field, { label: "Instruction (voice description)" },
          h("textarea", { className: "ov-textarea", value: form.instruct, onChange: upd("instruct"), rows: 3, placeholder: "male, american accent, moderate pitch" })),
        h(Field, { label: "Language" }, h(C.Input, { value: form.language, onChange: upd("language") })),
        h("label", { className: "ov-consent" },
          h("input", { type: "checkbox", checked: form.consent, onChange: upd("consent") }),
          h("span", null, "I consent to creating and using this synthetic voice.")),
        h(C.Button, { onClick: submit, disabled: props.busy }, props.busy ? "Creating\u2026" : "Create voice")
      )
    );
  }

  // ---- page ------------------------------------------------------------

  function VoicesPage() {
    var vs = useState({ voices: [], active: null, backend: "" });
    var state = vs[0], setState = vs[1];
    var es = useState("");           var err = es[0], setErr = es[1];
    var ns = useState("");           var note = ns[0], setNote = ns[1];
    var bs = useState(null);         var busyId = bs[0], setBusyId = bs[1];
    var fbs = useState(false);       var formBusy = fbs[0], setFormBusy = fbs[1];
    var ts = useState("voices");     var tab = ts[0], setTab = ts[1];
    var audioRef = useRef(null);

    var refresh = useCallback(function () {
      return api("/voices", {}).then(setState).catch(function (e) { setErr(e.message); });
    }, []);

    useEffect(function () { refresh(); }, [refresh]);

    var activate = function (id) {
      setBusyId(id); setErr(""); setNote("");
      jsonPost("/voices/" + id + "/active", { set_provider: false }, "PUT")
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
      h("div", { className: "ov-tabbar" },
        ["voices", "clone", "design"].map(function (t) {
          return h(C.Button, {
            key: t,
            variant: tab === t ? "default" : "secondary",
            className: "ov-tabbtn" + (tab === t ? " ov-tabbtn-on" : ""),
            onClick: function () { setTab(t); },
          }, t.charAt(0).toUpperCase() + t.slice(1));
        })
      ),
      tab === "voices"
        ? h(VoiceGrid, {
            voices: state.voices, busyId: busyId,
            onActivate: activate, onPreview: preview, onDelete: remove,
          })
        : null,
      tab === "clone"
        ? h(CloneForm, { busy: formBusy, onSubmit: onFormSubmit, onError: setErr })
        : null,
      tab === "design"
        ? h(DesignForm, { busy: formBusy, onSubmit: onFormSubmit, onError: setErr })
        : null,
      h("audio", { ref: audioRef, controls: true, className: "ov-audio" })
    );
  }

  window.__HERMES_PLUGINS__.register("omnivoice", VoicesPage);
})();
