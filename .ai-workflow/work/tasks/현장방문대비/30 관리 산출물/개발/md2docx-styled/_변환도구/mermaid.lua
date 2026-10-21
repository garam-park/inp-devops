-- Replace ```mermaid blocks with pre-rendered PNGs: <imgdir>/1.png, 2.png ... (in order of appearance)
function Pandoc(doc)
  local dir = pandoc.utils.stringify(doc.meta.imgdir or '')
  local n = 0
  doc.blocks = doc.blocks:walk({
    CodeBlock = function(cb)
      if cb.classes:includes('mermaid') then
        n = n + 1
        return pandoc.Para({ pandoc.Image({ pandoc.Str('다이어그램 ' .. n) }, dir .. '/' .. n .. '.png') })
      end
    end,
  })
  return doc
end
