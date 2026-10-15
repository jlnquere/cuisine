import fs from "node:fs/promises"
import path from "node:path"
import sharp from "sharp"

// Only the exported copy is resized; the vault keeps its original photos.
async function optimize(directory) {
  let count = 0
  for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name)
    if (entry.isDirectory()) {
      count += await optimize(file)
    } else if (/\.(jpg|png|webp)$/i.test(file)) {
      const input = await fs.readFile(file)
      const pipeline = sharp(input).rotate().resize({
        width: 1600, height: 1600, fit: "inside", withoutEnlargement: true,
      })
      const output = await (/\.png$/i.test(file)
        ? pipeline.png({ compressionLevel: 6 })
        : /\.webp$/i.test(file)
          ? pipeline.webp({ quality: 82 })
          : pipeline.jpeg({ quality: 82, mozjpeg: true })).toBuffer()
      if (output.length < input.length) await fs.writeFile(file, output)
      count++
    }
  }
  return count
}
console.log(`Images optimisées : ${await optimize("content")}`)
