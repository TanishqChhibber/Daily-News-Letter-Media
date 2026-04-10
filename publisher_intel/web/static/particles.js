const canvas = document.getElementById('bg');
const ctx = canvas.getContext('2d');
let w, h, particles;

function reset(){
  w = canvas.width = window.innerWidth;
  h = canvas.height = window.innerHeight;
  particles = Array.from({length: 150},()=>({
    x: Math.random()*w,
    y: Math.random()*h,
    vx: (Math.random()*2-1)*0.5,
    vy: (Math.random()*2-1)*0.5,
    r: Math.random()*2+0.5
  }));
}

function draw(){
  ctx.clearRect(0,0,w,h);
  // gradient background already via CSS
  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  for(const p of particles){
    p.x += p.vx; p.y += p.vy;
    if(p.x<0||p.x>w) p.vx*=-1;
    if(p.y<0||p.y>h) p.vy*=-1;
    ctx.beginPath();
    ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx.fill();
  }
  // grid lines
  ctx.strokeStyle = 'rgba(130,170,255,0.15)';
  ctx.lineWidth = 1;
  for(let gx=0; gx<w; gx+=80){
    ctx.beginPath(); ctx.moveTo(gx,0); ctx.lineTo(gx,h); ctx.stroke();
  }
  for(let gy=0; gy<h; gy+=80){
    ctx.beginPath(); ctx.moveTo(0,gy); ctx.lineTo(w,gy); ctx.stroke();
  }
  requestAnimationFrame(draw);
}

window.addEventListener('resize', reset);
reset();
draw();
