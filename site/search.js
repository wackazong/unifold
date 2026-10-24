/* The search of unifold.md. site/build.py writes the index, one entry per section: [address, page,
   heading, text]. This file searches it in the browser as you type: in the field in the header of every
   page, which shows the best sections under it, and on /search, which shows all of them. */
"use strict";
(() => {
  const wordStart = "(?<![\\p{L}\\p{N}])";            // a term matches the beginning of a word
  const escape = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  let loading = null;

  // The index, fetched the first time someone searches; revalidated, since its address never changes.
  function entries() {
    loading ??= fetch("/search.json", { cache: "no-cache" })
      .then((r) => { if (!r.ok) throw new Error(r.statusText); return r.json(); })
      .then((data) => data.map(([url, page, heading, text]) => ({ url, page, heading, text })))
      .catch((err) => { loading = null; throw err; });
    return loading;
  }

  // A section is found when every term is in it. Terms in the heading weigh most, then the
  // name of the page, then each time the term occurs in the text; the whole query in the heading
  // or the text weighs extra.
  function rank(e, terms, phrase) {
    let score = 0;
    for (const re of terms) {
      const inHeading = e.heading.search(re) >= 0, inPage = e.page.search(re) >= 0;
      const n = (e.text.match(re) || []).length;
      if (!inHeading && !inPage && !n) return 0;
      score += (inHeading ? 12 : 0) + (inPage ? 3 : 0) + Math.min(n, 10);
    }
    if (phrase && e.heading.toLowerCase().includes(phrase)) score += 20;
    else if (phrase && e.text.toLowerCase().includes(phrase)) score += 5;
    return score;
  }

  function search(index, q) {
    const words = [...new Set(q.toLowerCase().split(/\s+/))].sort((a, b) => b.length - a.length);
    const terms = words.map((w) => new RegExp(wordStart + escape(w), "giu"));
    const phrase = words.length > 1 ? q.toLowerCase().replace(/\s+/g, " ") : "";
    const hits = index
      .map((e, i) => ({ e, i, score: rank(e, terms, phrase) }))
      .filter((h) => h.score > 0)
      .sort((a, b) => b.score - a.score || a.i - b.i)
      .map((h) => h.e);
    const source = wordStart + "(?:" + words.map(escape).join("|") + ")";
    return { hits, all: new RegExp(source, "giu"), first: new RegExp(source, "iu") };
  }

  // A piece of the text around the first term found.
  function snippet(text, first, before, length) {
    const m = first.exec(text);
    const at = m ? m.index : 0;
    let start = Math.max(0, at - before);
    const space = text.indexOf(" ", start);
    if (start > 0 && space >= 0 && space < at) start = space + 1;
    let end = Math.min(text.length, start + length);
    if (end < text.length && text.lastIndexOf(" ", end) > at) end = text.lastIndexOf(" ", end);
    return (start > 0 ? "… " : "") + text.slice(start, end) + (end < text.length ? " …" : "");
  }

  function marked(text, all) {
    const out = document.createDocumentFragment();
    let last = 0;
    for (const m of text.matchAll(all)) {
      const mark = document.createElement("mark");
      mark.textContent = m[0];
      out.append(text.slice(last, m.index), mark);
      last = m.index + m[0].length;
    }
    out.append(text.slice(last));
    return out;
  }

  function element(tag, className, ...children) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    el.append(...children);
    return el;
  }

  function link(e, found) {
    const a = element("a", "", element("span", "crumb", e.page), element("span", "title", marked(e.heading, found.all)));
    a.href = e.url;
    return a;
  }

  // The field in the header: the best sections in a list under it, chosen with the arrow keys.
  function header(form) {
    const input = form.elements.q, button = form.querySelector("button");
    const list = element("ul", "hits");
    const shown = 8;
    list.id = "site-hits";
    list.hidden = true;
    list.setAttribute("role", "listbox");
    list.setAttribute("aria-label", "Sections found");
    form.append(list);
    Object.entries({ role: "combobox", "aria-controls": list.id, "aria-autocomplete": "list", "aria-expanded": "false" })
      .forEach(([k, v]) => input.setAttribute(k, v));
    const choices = () => list.querySelectorAll("[role=option]:not([aria-disabled])");
    let active = -1;

    function select(i) {
      active = i;
      choices().forEach((o, k) => o.setAttribute("aria-selected", String(k === i)));
      const o = choices()[i];
      if (o) {
        input.setAttribute("aria-activedescendant", o.id);
        o.scrollIntoView({ block: "nearest" });
      } else input.removeAttribute("aria-activedescendant");
    }

    function open(items) {
      items.forEach((li, i) => { li.id = `site-hit-${i}`; li.setAttribute("role", "option"); });
      list.replaceChildren(...items);
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
    }

    function close() {
      list.hidden = true;
      input.setAttribute("aria-expanded", "false");
      select(-1);
    }

    async function update() {
      const q = input.value.trim();
      if (!q) return close();
      let found;
      try {
        found = search(await entries(), q);
      } catch {
        const note = element("li", "note", "The index of the search could not be loaded.");
        note.setAttribute("aria-disabled", "true");
        return open([note]);
      }
      if (input.value.trim() !== q || document.activeElement !== input) return;  // overtaken
      const n = found.hits.length;
      const items = found.hits.slice(0, shown).map((e) => {
        const a = link(e, found);
        if (e.text) a.append(element("span", "snip", marked(snippet(e.text, found.first, 30, 120), found.all)));
        return element("li", "", a);
      });
      if (n > shown) {
        const more = element("a", "", `All ${n} sections`);
        more.href = "/search?q=" + encodeURIComponent(q);
        items.push(element("li", "more", more));
      }
      if (!n) {
        const note = element("li", "note", `Nothing found for “${q}”.`);
        note.setAttribute("aria-disabled", "true");
        items.push(note);
      }
      items.forEach((li) => li.querySelector("a")?.setAttribute("tabindex", "-1"));    // the field keeps the focus
      open(items);
      select(n ? 0 : -1);
    }

    input.addEventListener("input", update);
    input.addEventListener("focus", () => {
      entries().catch(() => {});
      if (input.value.trim()) update();
    });
    input.addEventListener("keydown", (ev) => {
      const n = choices().length;
      if ((ev.key === "ArrowDown" || ev.key === "ArrowUp") && !list.hidden && n) {
        ev.preventDefault();
        select((active + (ev.key === "ArrowDown" ? 1 : n - 1)) % n);
      } else if (ev.key === "Escape") {
        ev.preventDefault();
        if (!list.hidden) return close();
        input.value = "";
        input.blur();
      }
    });
    // Enter opens the chosen section; with nothing chosen, the form goes to /search.
    form.addEventListener("submit", (ev) => {
      const a = !list.hidden && choices()[active]?.querySelector("a");
      if (a) {
        ev.preventDefault();
        input.blur();
        location.href = a.href;
      }
    });
    // A click into the list must not take the focus from the field, or the list would close first.
    // After the click the list closes, also when the section is on this page.
    list.addEventListener("mousedown", (ev) => ev.preventDefault());
    list.addEventListener("click", (ev) => { if (ev.target.closest("a")) input.blur(); });
    form.addEventListener("focusout", (ev) => {
      if (form.contains(ev.relatedTarget)) return;
      close();
      form.classList.remove("open");
    });
    // On narrow screens only the button shows; it opens the field over the header.
    button.addEventListener("click", (ev) => {
      if (input.offsetWidth) return;
      ev.preventDefault();
      form.classList.add("open");
      input.focus();
    });
  }

  // The page /search: every section found, in full.
  function full(form) {
    const input = form.elements.q;
    const status = document.getElementById("search-status");
    const list = document.getElementById("results");
    const shown = 50;

    async function show() {
      const q = input.value.trim();
      history.replaceState(null, "", q ? "?q=" + encodeURIComponent(q) : location.pathname);
      document.title = q ? `${q} | Search | unifold` : "Search | unifold";
      if (!q) {
        list.replaceChildren();
        status.textContent = "Searches every section of the standard, the references, the explanations, the tutorial "
          + "and the start page.";
        return;
      }
      let found;
      try {
        found = search(await entries(), q);
      } catch {
        status.textContent = "The index of the search could not be loaded.";
        return;
      }
      if (input.value.trim() !== q) return;                                      // overtaken
      const n = found.hits.length;
      status.textContent = !n ? `Nothing found for “${q}”.`
        : `${n > shown ? `The first ${shown} of ${n}` : n} ${n === 1 ? "section" : "sections"} for “${q}”`;
      list.replaceChildren(...found.hits.slice(0, shown).map((e) => {
        const item = element("li", "", link(e, found));
        if (e.text) item.append(element("p", "", marked(snippet(e.text, found.first, 70, 220), found.all)));
        return item;
      }));
    }

    input.value = new URLSearchParams(location.search).get("q") || "";
    input.addEventListener("input", show);
    // Enter opens the first section found.
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      const top = list.querySelector("a");
      if (top) location.href = top.href;
    });
    show();
  }

  const bar = document.querySelector("form.site-search");
  if (bar) header(bar);
  const page = document.querySelector("form.search-big");
  if (page) full(page);
})();
