/**
 * Admin image crop tool.
 *
 * Attaches to any <input type="file" class="crop-enabled-input"> rendered
 * by CroppableImageWidget. When staff choose a new image file, a modal
 * opens with a draggable/resizable crop box and a row of aspect-ratio
 * presets (read from the input's data-crop-ratios attribute). Clicking
 * "Apply crop" draws the selected region onto a canvas and replaces the
 * input's file with the cropped result via DataTransfer — the rest of
 * the form (and the server) never knows the difference.
 *
 * This only ever runs on a freshly *selected* file, so opening an
 * existing saved image without changing it is completely unaffected.
 */
(function () {
  "use strict";

  function onReady(fn) {
    if (document.readyState !== "loading") {
      fn();
    } else {
      document.addEventListener("DOMContentLoaded", fn);
    }
  }

  function parseRatios(input) {
    try {
      var parsed = JSON.parse(input.dataset.cropRatios || "[]");
      return parsed.length ? parsed : [{ label: "Free", ratio: null }];
    } catch (e) {
      return [{ label: "Free", ratio: null }];
    }
  }

  function bindInput(input) {
    if (input.dataset.cropBound) return;
    input.dataset.cropBound = "true";
    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file || file.type.indexOf("image/") !== 0) return;
      openCropModal(input, file);
    });
  }

  function initCropInputs(root) {
    var scope = root || document;
    scope.querySelectorAll("input.crop-enabled-input[type=file]").forEach(bindInput);
  }

  function openCropModal(input, file) {
    var ratios = parseRatios(input);
    var reader = new FileReader();
    reader.onload = function (e) {
      var img = new Image();
      img.onload = function () {
        buildModal(input, file, img, ratios);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  function buildModal(input, originalFile, img, ratios) {
    var MAX_W = 640;
    var MAX_H = 440;
    var scale = Math.min(MAX_W / img.naturalWidth, MAX_H / img.naturalHeight, 1);
    var dispW = Math.max(1, Math.round(img.naturalWidth * scale));
    var dispH = Math.max(1, Math.round(img.naturalHeight * scale));

    var overlay = document.createElement("div");
    overlay.className = "crop-overlay";

    var modal = document.createElement("div");
    modal.className = "crop-modal";
    overlay.appendChild(modal);

    var header = document.createElement("div");
    header.className = "crop-modal-header";
    header.textContent = "Crop image before uploading";
    modal.appendChild(header);

    var stage = document.createElement("div");
    stage.className = "crop-stage";
    stage.style.width = dispW + "px";
    stage.style.height = dispH + "px";

    var imageEl = document.createElement("img");
    imageEl.className = "crop-stage-img";
    imageEl.src = img.src;
    imageEl.style.width = dispW + "px";
    imageEl.style.height = dispH + "px";
    imageEl.draggable = false;
    stage.appendChild(imageEl);

    var box = document.createElement("div");
    box.className = "crop-box";
    stage.appendChild(box);

    ["nw", "ne", "sw", "se"].forEach(function (pos) {
      var handle = document.createElement("div");
      handle.className = "crop-handle crop-handle-" + pos;
      handle.dataset.pos = pos;
      box.appendChild(handle);
    });

    var editView = document.createElement("div");
    editView.className = "crop-edit-view";
    editView.appendChild(stage);

    var ratioRow = document.createElement("div");
    ratioRow.className = "crop-ratio-row";
    editView.appendChild(ratioRow);

    var hint = document.createElement("div");
    hint.className = "crop-hint";
    hint.textContent = "Drag the box to move it, drag a corner to resize.";
    editView.appendChild(hint);

    modal.appendChild(editView);

    // Confirmation view: shown after "Apply crop" so staff can see exactly
    // what will be saved before it's committed to the file input.
    var confirmView = document.createElement("div");
    confirmView.className = "crop-confirm-view";
    confirmView.style.display = "none";

    var confirmLabel = document.createElement("div");
    confirmLabel.className = "crop-hint";
    confirmLabel.textContent = "This is exactly what will be saved:";
    confirmView.appendChild(confirmLabel);

    var confirmImg = document.createElement("img");
    confirmImg.className = "crop-confirm-img";
    confirmView.appendChild(confirmImg);

    modal.appendChild(confirmView);

    var footer = document.createElement("div");
    footer.className = "crop-modal-footer";
    modal.appendChild(footer);

    var btnCancel = document.createElement("button");
    btnCancel.type = "button";
    btnCancel.className = "crop-btn crop-btn-secondary";
    btnCancel.textContent = "Cancel";

    var btnOriginal = document.createElement("button");
    btnOriginal.type = "button";
    btnOriginal.className = "crop-btn crop-btn-secondary";
    btnOriginal.textContent = "Use original (no crop)";

    var btnApply = document.createElement("button");
    btnApply.type = "button";
    btnApply.className = "crop-btn crop-btn-primary";
    btnApply.textContent = "Apply crop";

    var btnBack = document.createElement("button");
    btnBack.type = "button";
    btnBack.className = "crop-btn crop-btn-secondary";
    btnBack.textContent = "Back to editing";
    btnBack.style.display = "none";

    var btnConfirm = document.createElement("button");
    btnConfirm.type = "button";
    btnConfirm.className = "crop-btn crop-btn-primary";
    btnConfirm.textContent = "Use this crop";
    btnConfirm.style.display = "none";

    footer.appendChild(btnCancel);
    footer.appendChild(btnOriginal);
    footer.appendChild(btnBack);
    footer.appendChild(btnApply);
    footer.appendChild(btnConfirm);

    document.body.appendChild(overlay);
    document.body.classList.add("crop-modal-open");

    // ---- box geometry helpers -------------------------------------------------

    var state = { ratio: ratios[0].ratio };

    function setBox(x, y, w, h) {
      box.style.left = x + "px";
      box.style.top = y + "px";
      box.style.width = w + "px";
      box.style.height = h + "px";
    }

    function getBox() {
      return {
        x: parseFloat(box.style.left) || 0,
        y: parseFloat(box.style.top) || 0,
        w: parseFloat(box.style.width) || 0,
        h: parseFloat(box.style.height) || 0,
      };
    }

    function layoutBoxForRatio(ratio) {
      var w, h;
      if (ratio) {
        w = dispW;
        h = w / ratio;
        if (h > dispH) {
          h = dispH;
          w = h * ratio;
        }
        w *= 0.9;
        h *= 0.9;
      } else {
        w = dispW * 0.8;
        h = dispH * 0.8;
      }
      setBox((dispW - w) / 2, (dispH - h) / 2, w, h);
    }

    ratios.forEach(function (r, idx) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "crop-ratio-btn" + (idx === 0 ? " active" : "");
      btn.textContent = r.label;
      btn.addEventListener("click", function () {
        ratioRow.querySelectorAll(".crop-ratio-btn").forEach(function (b) {
          b.classList.remove("active");
        });
        btn.classList.add("active");
        state.ratio = r.ratio;
        layoutBoxForRatio(r.ratio);
      });
      ratioRow.appendChild(btn);
    });

    layoutBoxForRatio(state.ratio);

    // ---- dragging / resizing ---------------------------------------------------

    var drag = null;
    var MIN_SIZE = 24;

    function clampMove(b) {
      return {
        x: Math.max(0, Math.min(b.x, dispW - b.w)),
        y: Math.max(0, Math.min(b.y, dispH - b.h)),
        w: b.w,
        h: b.h,
      };
    }

    function resizeBox(start, handlePos, dx, dy, ratio) {
      var x = start.x, y = start.y, w = start.w, h = start.h;

      if (handlePos.indexOf("e") !== -1) w = start.w + dx;
      if (handlePos.indexOf("s") !== -1) h = start.h + dy;
      if (handlePos.indexOf("w") !== -1) {
        w = start.w - dx;
        x = start.x + dx;
      }
      if (handlePos.indexOf("n") !== -1) {
        h = start.h - dy;
        y = start.y + dy;
      }

      w = Math.max(MIN_SIZE, w);
      h = Math.max(MIN_SIZE, h);

      if (ratio) {
        h = w / ratio;
        if (handlePos.indexOf("n") !== -1) {
          y = start.y + start.h - h;
        }
        if (handlePos.indexOf("w") !== -1) {
          x = start.x + start.w - w;
        }
      }

      // Clamp to stage bounds, preserving ratio if set.
      if (x < 0) {
        w += x;
        x = 0;
        if (ratio) h = w / ratio;
      }
      if (y < 0) {
        h += y;
        y = 0;
        if (ratio) w = h * ratio;
      }
      if (x + w > dispW) {
        w = dispW - x;
        if (ratio) h = w / ratio;
      }
      if (y + h > dispH) {
        h = dispH - y;
        if (ratio) w = h * ratio;
      }

      return { x: x, y: y, w: Math.max(MIN_SIZE, w), h: Math.max(MIN_SIZE, h) };
    }

    function onPointerMove(e) {
      if (!drag) return;
      var dx = e.clientX - drag.startX;
      var dy = e.clientY - drag.startY;
      if (drag.mode === "move") {
        var moved = clampMove({ x: drag.box.x + dx, y: drag.box.y + dy, w: drag.box.w, h: drag.box.h });
        setBox(moved.x, moved.y, moved.w, moved.h);
      } else {
        var resized = resizeBox(drag.box, drag.handle, dx, dy, state.ratio);
        setBox(resized.x, resized.y, resized.w, resized.h);
      }
    }

    function onPointerUp() {
      drag = null;
      document.removeEventListener("pointermove", onPointerMove);
      document.removeEventListener("pointerup", onPointerUp);
    }

    function startDrag(e, mode, handlePos) {
      drag = { mode: mode, handle: handlePos, startX: e.clientX, startY: e.clientY, box: getBox() };
      document.addEventListener("pointermove", onPointerMove);
      document.addEventListener("pointerup", onPointerUp);
      e.preventDefault();
    }

    box.addEventListener("pointerdown", function (e) {
      if (e.target.classList.contains("crop-handle")) return;
      startDrag(e, "move");
    });

    box.querySelectorAll(".crop-handle").forEach(function (handle) {
      handle.addEventListener("pointerdown", function (e) {
        e.stopPropagation();
        startDrag(e, "resize", handle.dataset.pos);
      });
    });

    // ---- modal lifecycle --------------------------------------------------

    function closeModal() {
      if (confirmImg.src) {
        URL.revokeObjectURL(confirmImg.src);
      }
      overlay.remove();
      document.body.classList.remove("crop-modal-open");
      document.removeEventListener("keydown", onKeydown);
    }

    function onKeydown(e) {
      if (e.key === "Escape") {
        input.value = "";
        closeModal();
      }
    }
    document.addEventListener("keydown", onKeydown);

    overlay.addEventListener("mousedown", function (e) {
      if (e.target === overlay) {
        input.value = "";
        closeModal();
      }
    });

    btnCancel.addEventListener("click", function () {
      input.value = "";
      closeModal();
    });

    btnOriginal.addEventListener("click", function () {
      closeModal();
    });

    var pendingBlob = null;
    var pendingMimeType = null;

    function showEditView() {
      editView.style.display = "";
      confirmView.style.display = "none";
      btnCancel.style.display = "";
      btnOriginal.style.display = "";
      btnApply.style.display = "";
      btnBack.style.display = "none";
      btnConfirm.style.display = "none";
    }

    function showConfirmView() {
      editView.style.display = "none";
      confirmView.style.display = "";
      btnCancel.style.display = "none";
      btnOriginal.style.display = "none";
      btnApply.style.display = "none";
      btnBack.style.display = "";
      btnConfirm.style.display = "";
    }

    btnApply.addEventListener("click", function () {
      var b = getBox();
      var scaleBack = img.naturalWidth / dispW;
      var sx = b.x * scaleBack;
      var sy = b.y * scaleBack;
      var sw = b.w * scaleBack;
      var sh = b.h * scaleBack;

      var canvas = document.createElement("canvas");
      canvas.width = Math.max(1, Math.round(sw));
      canvas.height = Math.max(1, Math.round(sh));
      var ctx = canvas.getContext("2d");
      ctx.drawImage(img, sx, sy, sw, sh, 0, 0, canvas.width, canvas.height);

      var mimeType =
        originalFile.type === "image/png" || originalFile.type === "image/webp"
          ? originalFile.type
          : "image/jpeg";
      var quality = mimeType === "image/jpeg" ? 0.92 : undefined;

      canvas.toBlob(
        function (blob) {
          if (!blob) return;
          pendingBlob = blob;
          pendingMimeType = mimeType;
          confirmImg.src = URL.createObjectURL(blob);
          showConfirmView();
        },
        mimeType,
        quality
      );
    });

    btnBack.addEventListener("click", function () {
      pendingBlob = null;
      showEditView();
    });

    btnConfirm.addEventListener("click", function () {
      if (!pendingBlob) {
        closeModal();
        return;
      }
      var croppedFile = new File([pendingBlob], originalFile.name, {
        type: pendingMimeType,
        lastModified: Date.now(),
      });
      var dt = new DataTransfer();
      dt.items.add(croppedFile);
      input.files = dt.files;
      closeModal();
    });
  }

  onReady(function () {
    initCropInputs(document);
  });

  // Django admin inline formsets can add new rows (e.g. "Add another")
  // after page load; re-scan for crop-enabled inputs when that happens.
  document.addEventListener("formset:added", function (event) {
    initCropInputs(event.target || document);
  });
})();
