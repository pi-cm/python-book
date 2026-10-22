--[[
원고 마크다운의 관례를 책 디자인 요소(pdf-header.tex의 매크로·환경)에 연결하는 pandoc 필터.

- "# Chapter 3. 제목"  → 장 번호를 3으로 맞추고 제목만 남김 (장 표지는 titlesec이 그림)
- 그 밖의 "# 제목"    → 번호 없는 장 (레퍼런스·부록)
- "## 3.1 제목"        → 절 번호를 \booksecnum{3.1}로 감싸 색을 입힘
- 인용 블록            → 첫 굵은 글씨로 종류를 판별해 상자 환경으로 감쌈
    **학습 목표** → goalsbox / **Q. …** → qabox / 그 밖의 굵은 제목 → tipbox / 나머지 → notebox
- 구분선(---)          → \bookrule (토큰 line 색의 짧은 선)
- 한자(CJK 통합 한자)   → \hanja{…} (본문 글꼴 고운바탕에 한자가 없어 명조로 찍음)
- 표 안의 인라인 코드  → . _ ( , 뒤에서 줄을 바꿀 수 있게 (옆 칸으로 넘치지 않게)
- 책 글꼴에 없는 문자(태국 문자, ▁, U+FFFD) → 대체 글꼴로 감쌈 (본문·인라인 코드·코드 블록)
]]

local CHAPTER_PATTERN = "^Chapter%s+(%d+)[%.:]%s*"
local SECTION_NUMBER_PATTERN = "^(%d+%.%d+)$"

-- 책 글꼴(D2Coding, AppleMyungjo)에 없는 드문 한자
local RARE_CJK = { [0x5F28] = true, [0x768B] = true }

-- 책 글꼴에 없는 문자를 찍을 대체 글꼴 (pdf-header.tex에 정의)
local function fallback_font(cp)
  if cp >= 0x0E00 and cp <= 0x0E7F then
    return "\\thaifont"
  elseif (cp >= 0x2580 and cp <= 0x259F) or cp == 0xFFFD or cp == 0x207B then
    return "\\symfallback"
  elseif (cp >= 0x0590 and cp <= 0x06FF) or (cp >= 0xFB1D and cp <= 0xFDFF) or (cp >= 0xFE70 and cp <= 0xFEFF)
      or (cp >= 0x1E00 and cp <= 0x1EFF) or RARE_CJK[cp] then
    -- 히브리·아랍 문자, 베트남어 성조 글자, 책 글꼴에 없는 드문 한자 (14장 온도 1.5 출력)
    return "\\symfallback"
  end
  return nil
end

local function has_fallback(text)
  for _, cp in utf8.codes(text) do
    if fallback_font(cp) then
      return true
    end
  end
  return false
end


-- 제목의 인라인 목록 앞부분에서 "Chapter N." 접두어를 떼어 낸다
local function strip_chapter_prefix(inlines)
  local text = pandoc.utils.stringify(inlines)
  local number = text:match(CHAPTER_PATTERN)
  if not number then
    return nil
  end
  local prefix_words = 2 -- "Chapter", "N." 두 단어
  local rest, seen = pandoc.List(), 0
  for _, el in ipairs(inlines) do
    if seen < prefix_words then
      if el.t == "Str" then
        seen = seen + 1
      end
    elseif not (#rest == 0 and el.t == "Space") then
      rest:insert(el)
    end
  end
  return tonumber(number), rest
end

function Header(h)
  if h.level == 1 then
    local number, rest = strip_chapter_prefix(h.content)
    if number then
      h.content = rest
      return {
        pandoc.RawBlock("latex", string.format("\\setcounter{chapter}{%d}", number - 1)),
        h,
      }
    end
    -- "Chapter N."이 아닌 장(레퍼런스·부록)은 번호 없이 목차에만 올리고,
    -- 머리말의 장 이름도 직접 바꾼다(번호 없는 장은 \\chaptermark를 부르지 않는다)
    h.classes:insert("unnumbered")
    local title = pandoc.utils.stringify(h.content)
      :gsub("\\", "\\textbackslash{}")
      :gsub("([#%%&$_{}])", "\\%1")
      :gsub("~", "\\textasciitilde{}")
    return { h, pandoc.RawBlock("latex", "\\markboth{" .. title .. "}{" .. title .. "}") }
  elseif h.level == 2 then
    local first = h.content[1]
    if first and first.t == "Str" and first.text:match(SECTION_NUMBER_PATTERN) then
      h.content[1] = pandoc.RawInline("latex", "\\booksecnum{" .. first.text .. "}")
    end
  end
  return h
end

-- 인용 블록의 첫 문단이 굵은 글씨로 시작하면 그 글씨를 반환한다
local function leading_strong(blocks)
  local first = blocks[1]
  if first and (first.t == "Para" or first.t == "Plain") then
    local el = first.content[1]
    if el and el.t == "Strong" then
      return pandoc.utils.stringify(el)
    end
  end
  return nil
end

local function wrap(env, blocks)
  local out = pandoc.List({ pandoc.RawBlock("latex", "\\begin{" .. env .. "}") })
  out:extend(blocks)
  out:insert(pandoc.RawBlock("latex", "\\end{" .. env .. "}"))
  return out
end

function BlockQuote(bq)
  local label = leading_strong(bq.content)
  if label == nil then
    return wrap("notebox", bq.content)
  elseif label:match("^학습%s*목표") then
    return wrap("goalsbox", bq.content)
  elseif label:match("^Q%.") then
    return wrap("qabox", bq.content)
  end
  return wrap("tipbox", bq.content)
end

function HorizontalRule()
  return pandoc.RawBlock("latex", "\\bookrule")
end

-- 한자 범위(U+3400–U+9FFF, U+F900–U+FAFF)가 들어 있는 낱말만 \hanja{}로 감싼다
local function has_hanja(text)
  for _, cp in utf8.codes(text) do
    if (cp >= 0x3400 and cp <= 0x9FFF) or (cp >= 0xF900 and cp <= 0xFAFF) then
      return true
    end
  end
  return false
end

function Str(el)
  if not FORMAT:match("latex") or not (has_hanja(el.text) or has_fallback(el.text)) then
    return nil
  end
  local out = pandoc.List()
  local buf, in_hanja = {}, false
  local function flush()
    if #buf == 0 then return end
    local chunk = table.concat(buf)
    if in_hanja then
      out:insert(pandoc.RawInline("latex", "\\hanja{" .. chunk .. "}"))
    else
      out:insert(pandoc.Str(chunk))
    end
    buf = {}
  end
  for _, cp in utf8.codes(el.text) do
    local font = fallback_font(cp)
    if font then
      flush()
      -- 바로 앞이 같은 글꼴로 감싼 덩어리면 그 안에 이어 붙인다 (결합 문자가 떨어지지 않게)
      local last = out[#out]
      local opener = "{" .. font .. " "
      if last and last.t == "RawInline" and last.text:sub(1, #opener) == opener then
        last.text = last.text:sub(1, -2) .. utf8.char(cp) .. "}"
      else
        out:insert(pandoc.RawInline("latex", opener .. utf8.char(cp) .. "}"))
      end
      goto continue
    end
    local is_h = (cp >= 0x3400 and cp <= 0x9FFF) or (cp >= 0xF900 and cp <= 0xFAFF)
    if is_h ~= in_hanja then
      flush()
      in_hanja = is_h
    end
    buf[#buf + 1] = utf8.char(cp)
    ::continue::
  end
  flush()
  return out
end

-- 표 칸 안의 인라인 코드는 줄을 바꾸지 못해 옆 칸으로 넘친다.
-- LaTeX 특수 문자를 이스케이프하고 . _ ( , 뒤에 줄바꿈 가능 지점을 넣는다.
local LATEX_ESCAPES = {
  ["\\"] = "\\textbackslash{}", ["{"] = "\\{", ["}"] = "\\}", ["_"] = "\\_",
  ["#"] = "\\#", ["%"] = "\\%", ["&"] = "\\&", ["$"] = "\\$",
  ["~"] = "\\textasciitilde{}", ["^"] = "\\textasciicircum{}",
}
local BREAK_AFTER = { ["."] = true, ["_"] = true, ["("] = true, [","] = true }

-- 코드 글자를 LaTeX로 옮긴다: 특수 문자 이스케이프, 대체 글꼴 감싸기, (원하면) 줄바꿈 지점
local function latex_code_chars(text, escapes, allow_breaks)
  -- 같은 대체 글꼴 문자가 이어지면 한 덩어리로 감싼다 (태국 문자의 결합 모음이 앞 글자에 붙도록)
  local out, run, run_font = {}, {}, nil
  local function close_run()
    if run_font then
      out[#out + 1] = "{" .. run_font .. " " .. table.concat(run) .. "}"
      run, run_font = {}, nil
    end
  end
  for _, cp in utf8.codes(text) do
    local ch = utf8.char(cp)
    local font = fallback_font(cp)
    if font then
      if font ~= run_font then
        close_run()
        run_font = font
      end
      run[#run + 1] = ch
    else
      close_run()
      out[#out + 1] = escapes[ch] or ch
      if allow_breaks and BREAK_AFTER[ch] then
        out[#out + 1] = "\\allowbreak{}"
      end
    end
  end
  close_run()
  return table.concat(out)
end

local function breakable_code(text)
  return "\\texttt{" .. latex_code_chars(text, LATEX_ESCAPES, true) .. "}"
end

-- 코드 블록(Highlighting 환경, commandchars=\\\{\}) 안에서는 \ { } 만 이스케이프한다
local VERBATIM_ESCAPES = { ["\\"] = "\\textbackslash{}", ["{"] = "\\{", ["}"] = "\\}" }

function CodeBlock(cb)
  if not FORMAT:match("latex") or not has_fallback(cb.text) then
    return nil
  end
  local body = latex_code_chars(cb.text, VERBATIM_ESCAPES, false)
  return pandoc.RawBlock("latex",
    "\\begin{Shaded}\n\\begin{Highlighting}[]\n" .. body .. "\n\\end{Highlighting}\n\\end{Shaded}")
end

function Code(c)
  if not FORMAT:match("latex") or not has_fallback(c.text) then
    return nil
  end
  return pandoc.RawInline("latex", "\\texttt{" .. latex_code_chars(c.text, LATEX_ESCAPES, false) .. "}")
end

function Table(tbl)
  if not FORMAT:match("latex") then
    return nil
  end
  return tbl:walk({
    Code = function(c)
      return pandoc.RawInline("latex", breakable_code(c.text))
    end,
  })
end
