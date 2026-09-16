// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "OrukeetDictation",
    platforms: [
        .macOS(.v13),
    ],
    products: [
        .executable(name: "orukeet-dictation", targets: ["OrukeetDictation"]),
        .library(name: "OrukeetDictationCore", targets: ["OrukeetDictationCore"]),
    ],
    targets: [
        .target(
            name: "OrukeetDictationCore"
        ),
        .executableTarget(
            name: "OrukeetDictation",
            dependencies: ["OrukeetDictationCore"]
        ),
        .testTarget(
            name: "OrukeetDictationCoreTests",
            dependencies: ["OrukeetDictationCore"]
        ),
    ]
)
