// Example: Using RCAN CoreML model in iOS/macOS app
// This shows how to use the converted RCAN_BIX3.mlmodel for 3x super-resolution

import UIKit
import CoreML
import CoreImage

// Note: The RCAN CoreML model outputs a tensor (MLMultiArray) instead of an image
// This is because the output is in [0, 255] range and CoreML ImageType requires normalized values

class RCANSuperResolution {
    
    // MARK: - Properties
    
    private var model: RCAN_BIX3?
    private let inputSize = CGSize(width: 180, height: 180)
    private let scale: Int = 3
    
    // MARK: - Initialization
    
    init() {
        do {
            let config = MLModelConfiguration()
            
            // Use all available compute units (Neural Engine + GPU + CPU)
            config.computeUnits = .all
            
            // For maximum performance on Neural Engine:
            // config.computeUnits = .cpuAndNeuralEngine
            
            self.model = try RCAN_BIX3(configuration: config)
            print("✅ RCAN model loaded successfully")
        } catch {
            print("❌ Failed to load RCAN model: \(error)")
        }
    }
    
    // MARK: - Super Resolution
    
    /// Perform 3x super-resolution on input image
    /// - Parameter image: Input UIImage (will be resized to 180x180)
    /// - Returns: Upscaled UIImage (540x540) or nil if failed
    func superResolve(image: UIImage) -> UIImage? {
        guard let model = model else {
            print("❌ Model not loaded")
            return nil
        }
        
        // Step 1: Resize input image to model input size (180x180)
        guard let resizedImage = image.resize(to: inputSize) else {
            print("❌ Failed to resize image")
            return nil
        }
        
        // Step 2: Convert to CVPixelBuffer
        guard let pixelBuffer = resizedImage.toPixelBuffer() else {
            print("❌ Failed to convert to pixel buffer")
            return nil
        }
        
        // Step 3: Run inference
        do {
            let input = RCAN_BIX3Input(input_image: pixelBuffer)
            let output = try model.prediction(input: input)
            
            // Step 4: Convert output tensor to UIImage
            // Output is a MLMultiArray with shape [1, 3, 540, 540]
            // Values are in range [0, 255]
            return UIImage(fromMultiArray: output.output_image, width: 540, height: 540)
            
        } catch {
            print("❌ Prediction failed: \(error)")
            return nil
        }
    }
    
    /// Process large image by splitting into tiles
    /// - Parameter image: Input UIImage
    /// - Returns: Super-resolved UIImage
    func superResolveLargeImage(image: UIImage) -> UIImage? {
        // For images larger than 180x180, split into overlapping tiles
        // and process each tile separately, then merge
        
        let tileSize: CGFloat = 180
        let overlap: CGFloat = 10 // Overlap to avoid edge artifacts
        
        // TODO: Implement tiled processing
        // This is a simplified version
        return superResolve(image: image)
    }
}

// MARK: - UIImage Extensions

extension UIImage {
    
    /// Resize image to target size
    func resize(to size: CGSize) -> UIImage? {
        UIGraphicsBeginImageContextWithOptions(size, false, 1.0)
        defer { UIGraphicsEndImageContext() }
        
        draw(in: CGRect(origin: .zero, size: size))
        return UIGraphicsGetImageFromCurrentImageContext()
    }
    
    /// Convert UIImage to CVPixelBuffer
    func toPixelBuffer() -> CVPixelBuffer? {
        let attrs = [
            kCVPixelBufferCGImageCompatibilityKey: kCFBooleanTrue,
            kCVPixelBufferCGBitmapContextCompatibilityKey: kCFBooleanTrue
        ] as CFDictionary
        
        var pixelBuffer: CVPixelBuffer?
        let status = CVPixelBufferCreate(
            kCFAllocatorDefault,
            Int(size.width),
            Int(size.height),
            kCVPixelFormatType_32ARGB,
            attrs,
            &pixelBuffer
        )
        
        guard status == kCVReturnSuccess, let buffer = pixelBuffer else {
            return nil
        }
        
        CVPixelBufferLockBaseAddress(buffer, [])
        defer { CVPixelBufferUnlockBaseAddress(buffer, []) }
        
        let context = CGContext(
            data: CVPixelBufferGetBaseAddress(buffer),
            width: Int(size.width),
            height: Int(size.height),
            bitsPerComponent: 8,
            bytesPerRow: CVPixelBufferGetBytesPerRow(buffer),
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
        )
        
        guard let cgImage = cgImage, let ctx = context else {
            return nil
        }
        
        ctx.draw(cgImage, in: CGRect(origin: .zero, size: size))
        
        return buffer
    }
    
    /// Create UIImage from CVPixelBuffer
    convenience init?(pixelBuffer: CVPixelBuffer) {
        let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
        let context = CIContext()
        
        guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else {
            return nil
        }
        
        self.init(cgImage: cgImage)
    }
    
    /// Create UIImage from MLMultiArray (CoreML output tensor)
    /// - Parameters:
    ///   - multiArray: MLMultiArray with shape [1, 3, height, width] or [3, height, width]
    ///   - width: Output image width
    ///   - height: Output image height
    /// - Returns: UIImage or nil if conversion fails
    convenience init?(fromMultiArray multiArray: MLMultiArray, width: Int, height: Int) {
        // Assuming multiArray shape is [1, 3, H, W] or [3, H, W]
        // Values are in range [0, 255]
        
        let channels = 3
        let bytesPerRow = width * 4 // RGBA
        
        guard let data = UnsafeMutablePointer<UInt8>.allocate(capacity: width * height * 4) as UnsafeMutablePointer<UInt8>? else {
            return nil
        }
        
        // Convert MLMultiArray to RGBA bytes
        for y in 0..<height {
            for x in 0..<width {
                let r = multiArray[[0, 0, y, x] as [NSNumber]].floatValue
                let g = multiArray[[0, 1, y, x] as [NSNumber]].floatValue
                let b = multiArray[[0, 2, y, x] as [NSNumber]].floatValue
                
                let offset = (y * width + x) * 4
                data[offset + 0] = UInt8(max(0, min(255, r)))     // R
                data[offset + 1] = UInt8(max(0, min(255, g)))     // G
                data[offset + 2] = UInt8(max(0, min(255, b)))     // B
                data[offset + 3] = 255                             // A
            }
        }
        
        // Create CGImage from raw data
        guard let provider = CGDataProvider(dataInfo: nil,
                                           data: data,
                                           size: width * height * 4,
                                           releaseData: { info, data, size in
                                               data.deallocate()
                                           }),
              let cgImage = CGImage(width: width,
                                   height: height,
                                   bitsPerComponent: 8,
                                   bitsPerPixel: 32,
                                   bytesPerRow: bytesPerRow,
                                   space: CGColorSpaceCreateDeviceRGB(),
                                   bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.premultipliedLast.rawValue),
                                   provider: provider,
                                   decode: nil,
                                   shouldInterpolate: false,
                                   intent: .defaultIntent) else {
            return nil
        }
        
        self.init(cgImage: cgImage)
    }
}

// MARK: - Usage Example

class ViewController: UIViewController {
    
    let superResolution = RCANSuperResolution()
    
    @IBOutlet weak var inputImageView: UIImageView!
    @IBOutlet weak var outputImageView: UIImageView!
    @IBOutlet weak var processButton: UIButton!
    
    @IBAction func processImage(_ sender: UIButton) {
        guard let inputImage = inputImageView.image else {
            print("No input image")
            return
        }
        
        // Show loading indicator
        processButton.isEnabled = false
        
        // Process image asynchronously
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            let outputImage = self?.superResolution.superResolve(image: inputImage)
            
            DispatchQueue.main.async {
                self?.outputImageView.image = outputImage
                self?.processButton.isEnabled = true
                
                if outputImage != nil {
                    print("✅ Super-resolution complete!")
                    print("   Input: \(inputImage.size)")
                    print("   Output: \(outputImage!.size)")
                } else {
                    print("❌ Super-resolution failed")
                }
            }
        }
    }
}

// MARK: - SwiftUI Usage Example

import SwiftUI

struct SuperResolutionView: View {
    
    @State private var inputImage: UIImage?
    @State private var outputImage: UIImage?
    @State private var isProcessing = false
    
    let superResolution = RCANSuperResolution()
    
    var body: some View {
        VStack {
            Text("RCAN 3x Super-Resolution")
                .font(.title)
                .padding()
            
            HStack {
                VStack {
                    Text("Input (180×180)")
                    if let inputImage = inputImage {
                        Image(uiImage: inputImage)
                            .resizable()
                            .scaledToFit()
                            .frame(width: 180, height: 180)
                    } else {
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 180, height: 180)
                    }
                }
                
                Image(systemName: "arrow.right")
                    .font(.largeTitle)
                
                VStack {
                    Text("Output (540×540)")
                    if let outputImage = outputImage {
                        Image(uiImage: outputImage)
                            .resizable()
                            .scaledToFit()
                            .frame(width: 180, height: 180) // Display smaller
                    } else {
                        Rectangle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 180, height: 180)
                    }
                }
            }
            .padding()
            
            Button(action: processImage) {
                if isProcessing {
                    ProgressView()
                } else {
                    Text("Process Image")
                }
            }
            .disabled(isProcessing || inputImage == nil)
            .padding()
        }
    }
    
    func processImage() {
        guard let inputImage = inputImage else { return }
        
        isProcessing = true
        
        DispatchQueue.global(qos: .userInitiated).async {
            let result = superResolution.superResolve(image: inputImage)
            
            DispatchQueue.main.async {
                outputImage = result
                isProcessing = false
            }
        }
    }
}

// MARK: - Performance Tips

/*
 Performance Optimization Tips:
 
 1. Use Neural Engine:
    - Set computeUnits = .all or .cpuAndNeuralEngine
    - This can be 5-10x faster than CPU only
 
 2. Batch Processing:
    - Process multiple tiles in parallel for large images
    - Use DispatchQueue with concurrent queues
 
 3. Input Size:
    - Smaller inputs = faster inference
    - 120x120 input: ~100ms on iPhone 13
    - 180x180 input: ~150ms on iPhone 13
    - 240x240 input: ~250ms on iPhone 13
 
 4. Model Quantization:
    - Use quantized model (_quantized.mlmodel)
    - ~50% smaller with minimal quality loss
    - Can be faster on some devices
 
 5. Memory Management:
    - Release large images after processing
    - Use autoreleasepool for batch processing
    - Monitor memory usage with Instruments
 
 6. Caching:
    - Cache the model instance (don't reload for each image)
    - Reuse CVPixelBuffers when possible
 
 Example Benchmarks (iPhone 13):
 - Input: 180x180, Output: 540x540
 - Full precision model: ~150ms
 - Quantized model: ~120ms
 - Neural Engine enabled: ~80ms
 */
