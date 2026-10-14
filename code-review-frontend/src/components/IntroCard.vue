<template>
  <section class="card card-hover p-6 mb-5 animate-fadeInUp">
    <div class="flex items-start gap-4">
      <div class="w-11 h-11 rounded-xl flex items-center justify-center flex-none" style="background: linear-gradient(135deg, var(--brand), var(--brand2)); color: #fff">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M2 12h4M18 12h4" /><circle cx="12" cy="12" r="7" /></svg>
      </div>
      <div>
        <h2 class="font-bold text-[16px] mb-1.5">关于本系统</h2>
        <p class="text-[14px] leading-relaxed" style="color: var(--text-2)">
          本系统结合 <b style="color: var(--text)">LLM 大模型</b> + <b style="color: var(--text)">规则引擎(Semgrep)</b> 进行代码深度审查，搭配 <b style="color: var(--text)">RAG 检索相似缺陷案例</b>，通过 <b style="color: var(--text)">Function Calling</b> 调用本地代码解析器，自动生成代码缺陷报告。
        </p>
        <div class="flex flex-wrap gap-2 mt-3">
          <span class="text-[11px] px-2.5 py-1 rounded-full font-medium" style="background: #eef7f1; color: #15803d">LLM 大模型</span>
          <span class="text-[11px] px-2.5 py-1 rounded-full font-medium" style="background: #eef3ff; color: var(--brand)">Semgrep 规则引擎</span>
          <span class="text-[11px] px-2.5 py-1 rounded-full font-medium" style="background: #f5f3ff; color: #7c3aed">RAG 检索</span>
          <span class="text-[11px] px-2.5 py-1 rounded-full font-medium" style="background: #fff7ed; color: #c2410c">Function Calling</span>
        </div>
      </div>
    </div>
  </section>
</template>
