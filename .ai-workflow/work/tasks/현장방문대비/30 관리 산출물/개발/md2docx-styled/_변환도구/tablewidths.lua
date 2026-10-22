-- Set table column widths proportional to content length (CJK counts double).
local function wlen(str)
  local n = 0
  for _, c in utf8.codes(str) do n = n + (c >= 0x1100 and 2 or 1) end
  return n
end
function Table(tbl)
  local ncols = #tbl.colspecs
  local mx, sum, cnt = {}, {}, {}
  for i = 1, ncols do mx[i], sum[i], cnt[i] = 0, 0, 0 end
  local function scan(rows)
    for _, row in ipairs(rows) do
      for i, cell in ipairs(row.cells) do
        if i <= ncols then
          local w = wlen(pandoc.utils.stringify(cell.contents))
          if w > mx[i] then mx[i] = w end
          sum[i] = sum[i] + w; cnt[i] = cnt[i] + 1
        end
      end
    end
  end
  scan(tbl.head.rows)
  for _, b in ipairs(tbl.bodies) do scan(b.body) end
  local weights, total = {}, 0
  for i = 1, ncols do
    local avg = cnt[i] > 0 and sum[i] / cnt[i] or 1
    local w = 0.5 * math.min(mx[i], 60) + 0.5 * math.min(avg, 60)
    if w < 8 then w = 8 end
    weights[i] = w; total = total + w
  end
  for i = 1, ncols do tbl.colspecs[i] = {tbl.colspecs[i][1], weights[i] / total} end
  return tbl
end
