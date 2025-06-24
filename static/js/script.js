document.addEventListener('DOMContentLoaded', () => {
  const btnFace = document.getElementById('btn-face');
  const btnSnap = document.getElementById('btn-snap');
  const btnRec  = document.getElementById('btn-rec');
  const status = document.getElementById('status');
  const countEl = document.getElementById('count');
  const snaps = document.getElementById('snaps');

  btnFace.addEventListener('click', () => {
    fetch('/toggle_face', { method: 'POST' });
  });

  btnSnap.addEventListener('click', () => {
    fetch('/snapshot', { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        if (data.saved) {
          const img = document.createElement('img');
          img.src = data.path;
          img.width = 160;
          snaps.prepend(img);
        } else {
          console.error('Snapshot not saved');
        }
      });
  });

  btnRec.addEventListener('click', () => {
    fetch('/toggle_record', { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        status.textContent = data.recording ? 'Đang ghi...' : 'Dừng ghi';
      });
  });

  // Poll số mặt mỗi giây
  setInterval(() => {
    fetch('/face_count')
      .then(res => res.json())
      .then(data => {
        countEl.textContent = data.count;
      });
  }, 1000);
});
