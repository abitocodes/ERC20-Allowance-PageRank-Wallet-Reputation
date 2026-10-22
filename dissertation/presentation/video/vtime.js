/* video/vtime.js — virtual time for frame-exact capture (injected before any page script).
   performance.now, Date, requestAnimationFrame, setTimeout and setInterval all run on a clock that
   moves only when the renderer calls __vt.advance(ms): timers that fall due run in order, then the
   queued animation-frame callbacks run once (GSAP's ticker, and with it every tween, deck loop and
   three.js scene), then CSS animations and transitions are set to the same clock. A frame captured
   after advance() is therefore the state at exactly that virtual time, however long the capture took. */
(function () {
  'use strict';
  var now = 0;
  var epoch = 1760000000000;                 /* fixed wall clock: renders do not depend on the day */
  var RealDate = Date;
  function VDate(a, b, c, d, e, f, g) {
    if (!(this instanceof VDate)) return new RealDate(epoch + now).toString();
    var n = arguments.length;
    return n === 0 ? new RealDate(epoch + now) : n === 1 ? new RealDate(a) : new RealDate(a, b, c == null ? 1 : c, d || 0, e || 0, f || 0, g || 0);
  }
  VDate.prototype = RealDate.prototype;
  VDate.now = function () { return epoch + now; };
  VDate.UTC = RealDate.UTC; VDate.parse = RealDate.parse;
  window.Date = VDate;
  try { performance.now = function () { return now; }; } catch (e) { /* read-only in some builds */ }
  Object.defineProperty(performance, 'now', { configurable: true, value: function () { return now; } });

  var rafQ = [], rafId = 0;
  window.requestAnimationFrame = function (cb) { rafQ.push({ id: ++rafId, cb: cb }); return rafId; };
  window.cancelAnimationFrame = function (id) { for (var i = 0; i < rafQ.length; i++) if (rafQ[i].id === id) { rafQ.splice(i, 1); return; } };

  var timers = [], tid = 0;
  function addTimer(fn, ms, args, every) {
    var id = ++tid;
    timers.push({ id: id, at: now + Math.max(0, +ms || 0), fn: fn, args: args, every: every });
    return id;
  }
  window.setTimeout = function (fn, ms) { return addTimer(fn, ms, Array.prototype.slice.call(arguments, 2), 0); };
  window.setInterval = function (fn, ms) { var p = Math.max(4, +ms || 0); return addTimer(fn, p, Array.prototype.slice.call(arguments, 2), p); };
  window.clearTimeout = window.clearInterval = function (id) { for (var i = 0; i < timers.length; i++) if (timers[i].id === id) { timers.splice(i, 1); return; } };

  function runTimersUntil(target) {
    for (var guard = 0; guard < 100000; guard++) {
      var best = -1;
      for (var i = 0; i < timers.length; i++) if (timers[i].at <= target && (best < 0 || timers[i].at < timers[best].at || (timers[i].at === timers[best].at && timers[i].id < timers[best].id))) best = i;
      if (best < 0) return;
      var t = timers[best];
      if (t.at > now) now = t.at;
      if (t.every) t.at += t.every; else timers.splice(best, 1);
      try { if (typeof t.fn === 'function') t.fn.apply(window, t.args); } catch (e) { (window.__vtErrors = window.__vtErrors || []).push(String(e && e.stack || e)); }
    }
  }
  function syncCSS() {
    if (!document.getAnimations) return;
    var list = document.getAnimations();
    for (var i = 0; i < list.length; i++) {
      var a = list[i];
      if (a.__vt0 === undefined) { a.__vt0 = now - (a.currentTime || 0); try { a.pause(); } catch (e) { /* ignore */ } }
      try { a.currentTime = now - a.__vt0; } catch (e) { /* ignore */ }
    }
  }
  window.__vt = {
    now: function () { return now; },
    /* move the clock by ms: timers, then one animation frame, then CSS animations */
    advance: function (ms) {
      var target = now + ms;
      runTimersUntil(target);
      now = target;
      var q = rafQ; rafQ = [];
      for (var i = 0; i < q.length; i++) { try { q[i].cb(now); } catch (e) { (window.__vtErrors = window.__vtErrors || []).push(String(e && e.stack || e)); } }
      syncCSS();
      return now;
    },
    pending: function () { return { raf: rafQ.length, timers: timers.length }; }
  };
})();
