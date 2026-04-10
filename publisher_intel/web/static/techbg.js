// Simple animated grid + dots background
const canvas = document.getElementById('bg');
const ctx = canvas.getContext('2d');
let w, h, dots = [];
function resize() {
  w = canvas.width = window.innerWidth;
  h = canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

function makeDots() {
  dots = [];
  for (let i = 0; i < 40; i++) {
    dots.push({
      x: Math.random() * w,
      y: Math.random() * h,
      r: 2 + Math.random() * 2,
      dx: (Math.random() - 0.5) * 0.4,
      dy: (Math.random() - 0.5) * 0.4
    });
  }
}
makeDots();

function drawGrid() {
  ctx.save();
  ctx.strokeStyle = "#1e90ff22";
  ctx.lineWidth = 1;
  for (let x = 0; x < w; x += 60) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, h);
    ctx.stroke();
  }
  for (let y = 0; y < h; y += 60) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }
  ctx.restore();
}
function drawDots() {
  for (let d of dots) {
    ctx.beginPath();
    ctx.arc(d.x, d.y, d.r, 0, 2 * Math.PI);
    ctx.fillStyle = "#00f2ff";
    ctx.shadowColor = "#00f2ff";
    ctx.shadowBlur = 8;
    ctx.fill();
    ctx.shadowBlur = 0;
    d.x += d.dx;
    d.y += d.dy;
    if (d.x < 0 || d.x > w) d.dx *= -1;
    if (d.y < 0 || d.y > h) d.dy *= -1;
  }
}
canvas.addEventListener('mousemove', e => {
  for (let d of dots) {
    let dist = Math.hypot(d.x - e.clientX, d.y - e.clientY);
    if (dist < 60) {
      d.dx += (d.x - e.clientX) * 0.0005;
      d.dy += (d.y - e.clientY) * 0.0005;
    }
  }
});
function animate() {
  ctx.clearRect(0, 0, w, h);
  drawGrid();
  drawDots();
  requestAnimationFrame(animate);
}
animate();
