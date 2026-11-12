// Deterministic document redaction. Original screenshots are never overwritten.
// JSON rectangles use the screenshot's top-left pixel coordinates.
import AppKit
import ImageIO
import Vision

struct Mask: Decodable {
    let x: Int, y: Int, width: Int, height: Int
    let color: String
    let label: String?
    let fontSize: Double?
    let bold: Bool?
    let textColor: String?
}
struct Asset: Decodable {
    let source: String, output: String
    let masks: [Mask]
    let cropHeight: Int?
    let weakMasks: [Mask]?
}
enum RedactionError: Error { case invalidInput(String) }

func removePrivateMetadata(_ path: String) throws {
    let url = URL(fileURLWithPath: path)
    let source = try Data(contentsOf: url)
    guard source.prefix(8) == Data([137, 80, 78, 71, 13, 10, 26, 10]) else {
        throw RedactionError.invalidInput("Expected PNG output")
    }
    var output = Data(source.prefix(8)), offset = 8
    while offset < source.count {
        guard offset + 12 <= source.count else { throw RedactionError.invalidInput("Truncated PNG") }
        let length = source[offset..<(offset + 4)].reduce(0) { ($0 << 8) | Int($1) }
        let end = offset + length + 12
        guard end <= source.count else { throw RedactionError.invalidInput("Truncated PNG chunk") }
        let type = String(data: source[(offset + 4)..<(offset + 8)], encoding: .ascii) ?? ""
        // Read chunk types only, never private metadata values. Pixel/color chunks retain their exact bytes.
        if !["eXIf", "tEXt", "iTXt", "zTXt"].contains(type) { output.append(source[offset..<end]) }
        offset = end
    }
    try output.write(to: url, options: .atomic)
}

func readImage(_ path: String) throws -> CGImage {
    guard let source = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        throw RedactionError.invalidInput("Cannot decode image: " + path)
    }
    return image
}

func recognize(_ image: CGImage) throws -> [[String: Any]] {
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["zh-Hans", "en-US"]
    request.usesLanguageCorrection = true
    try VNImageRequestHandler(cgImage: image, options: [:]).perform([request])
    return (request.results ?? []).compactMap { result in
        guard let candidate = result.topCandidates(1).first else { return nil }
        let rect = result.boundingBox
        return ["text": candidate.string, "confidence": candidate.confidence,
                "x": Int(floor(rect.minX * Double(image.width))),
                "y": Int(floor((1 - rect.maxY) * Double(image.height))),
                "width": Int(ceil(rect.width * Double(image.width))),
                "height": Int(ceil(rect.height * Double(image.height)))]
    }
}

func textContrast(_ image: CGImage) throws -> CGImage {
    // Analysis only: expand the near-white range to expose faint watermark text.
    let width = image.width, height = image.height
    guard let context = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8,
        bytesPerRow: width * 4, space: CGColorSpace(name: CGColorSpace.sRGB)!,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue), let data = context.data else {
        throw RedactionError.invalidInput("Cannot create OCR contrast view")
    }
    context.draw(image, in: CGRect(x: 0, y: 0, width: width, height: height))
    let pixels = data.bindMemory(to: UInt8.self, capacity: width * height * 4)
    for i in stride(from: 0, to: width * height * 4, by: 4) {
        let lightness = (Int(pixels[i]) + Int(pixels[i + 1]) + Int(pixels[i + 2])) / 3
        let adjusted = UInt8(max(0, min(255, (lightness - 235) * 13)))
        pixels[i] = adjusted; pixels[i + 1] = adjusted; pixels[i + 2] = adjusted
    }
    guard let result = context.makeImage() else { throw RedactionError.invalidInput("OCR contrast failed") }
    return result
}

func writeImage(_ image: CGImage, asset: Asset) throws {
    let width = image.width, height = asset.cropHeight ?? image.height
    guard height > 0, height <= image.height else { throw RedactionError.invalidInput("Invalid crop height") }
    guard let context = CGContext(data: nil, width: width, height: height, bitsPerComponent: 8,
        bytesPerRow: width * 4, space: CGColorSpace(name: CGColorSpace.sRGB)!,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else {
        throw RedactionError.invalidInput("Cannot create redaction canvas")
    }
    context.draw(image, in: CGRect(x: 0, y: height - image.height, width: width, height: image.height))
    if let regions = asset.weakMasks, let data = context.data {
        let pixels = data.bindMemory(to: UInt8.self, capacity: width * height * 4)
        for rect in regions {
            guard rect.x >= 0, rect.y >= 0, rect.width > 0, rect.height > 0,
                  rect.x + rect.width <= width, rect.y + rect.height <= height else {
                throw RedactionError.invalidInput("Invalid watermark region")
            }
            var frequencies: [UInt32: Int] = [:]
            for y in rect.y..<(rect.y + rect.height) {
                for x in rect.x..<(rect.x + rect.width) {
                    let i = (y * width + x) * 4
                    let rgb = UInt32(pixels[i]) << 16 | UInt32(pixels[i + 1]) << 8 | UInt32(pixels[i + 2])
                    frequencies[rgb, default: 0] += 1
                }
            }
            guard let background = frequencies.max(by: { $0.value < $1.value })?.key else { continue }
            let rgb = [UInt8((background >> 16) & 255), UInt8((background >> 8) & 255), UInt8(background & 255)]
            let allowedSpread = max(3, (Int(rgb.max()!) - Int(rgb.min()!)) / 2)
            for y in rect.y..<(rect.y + rect.height) {
                for x in rect.x..<(rect.x + rect.width) {
                    let i = (y * width + x) * 4
                    // Remove only the weak overlay close to this panel's own background.
                    // Strong labels, business values, icons and chart strokes remain.
                    let deltas = (0..<3).map { Int(rgb[$0]) - Int(pixels[i + $0]) }
                    if deltas.min()! >= 0, deltas.max()! <= 20,
                       deltas.max()! - deltas.min()! <= allowedSpread {
                        for c in 0..<3 { pixels[i + c] = rgb[c] }
                    }
                }
            }
        }
    }
    for mask in asset.masks {
        guard mask.x >= 0, mask.y >= 0, mask.width > 0, mask.height > 0,
              mask.x + mask.width <= width, mask.y + mask.height <= height,
              let value = UInt32(mask.color, radix: 16), mask.color.count == 6 else {
            throw RedactionError.invalidInput("Invalid rectangle in: " + asset.source)
        }
        context.setFillColor(CGColor(red: CGFloat((value >> 16) & 255) / 255,
                                     green: CGFloat((value >> 8) & 255) / 255,
                                     blue: CGFloat(value & 255) / 255, alpha: 1))
        context.fill(CGRect(x: mask.x, y: height - mask.y - mask.height,
                            width: mask.width, height: mask.height))
        if let label = mask.label {
            let textValue = UInt32(mask.textColor ?? "333333", radix: 16) ?? 0x333333
            let font = NSFont.systemFont(ofSize: mask.fontSize ?? 16,
                                         weight: mask.bold == true ? .semibold : .regular)
            let color = NSColor(srgbRed: CGFloat((textValue >> 16) & 255) / 255,
                                green: CGFloat((textValue >> 8) & 255) / 255,
                                blue: CGFloat(textValue & 255) / 255, alpha: 1)
            NSGraphicsContext.saveGraphicsState()
            NSGraphicsContext.current = NSGraphicsContext(cgContext: context, flipped: false)
            NSAttributedString(string: label, attributes: [.font: font, .foregroundColor: color])
                .draw(in: NSRect(x: mask.x + 4, y: height - mask.y - mask.height + 3,
                                  width: mask.width - 8, height: mask.height - 6))
            NSGraphicsContext.restoreGraphicsState()
        }
    }
    let outputURL = URL(fileURLWithPath: asset.output)
    try FileManager.default.createDirectory(at: outputURL.deletingLastPathComponent(),
                                            withIntermediateDirectories: true)
    guard let result = context.makeImage(),
          let destination = CGImageDestinationCreateWithURL(outputURL as CFURL, "public.png" as CFString, 1, nil) else {
        throw RedactionError.invalidInput("Cannot create output: " + asset.output)
    }
    // No original metadata, source strings or recovery layer accompany the flattened pixels.
    CGImageDestinationAddImage(destination, result, nil)
    guard CGImageDestinationFinalize(destination) else {
        throw RedactionError.invalidInput("Cannot save output: " + asset.output)
    }
    try removePrivateMetadata(asset.output)
}

do {
    let args = CommandLine.arguments
    if args.count == 3, ["ocr", "ocr-contrast"].contains(args[1]) {
        let source = try readImage(args[2])
        let result = try recognize(args[1] == "ocr-contrast" ? textContrast(source) : source)
        let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
        FileHandle.standardOutput.write(data)
    } else if args.count == 3, ["redact", "strip-metadata"].contains(args[1]) {
        let assets = try JSONDecoder().decode([Asset].self, from: Data(contentsOf: URL(fileURLWithPath: args[2])))
        for asset in assets {
            if args[1] == "strip-metadata" { try removePrivateMetadata(asset.output) }
            else { try writeImage(readImage(asset.source), asset: asset) }
            print("SANITIZED: " + asset.output)
        }
    } else {
        throw RedactionError.invalidInput("Usage: redact-client-screenshots ocr IMAGE | redact MANIFEST")
    }
} catch {
    fputs("Redaction failed: \(error)\n", stderr)
    exit(1)
}
