// swift-tools-version: 6.2
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "GraphitiClient",
    platforms: [
        .macOS(.v26),
        .iOS(.v26),
        .watchOS(.v26),
        .tvOS(.v26),
        .visionOS(.v26)
    ],
    products: [
        .library(
            name: "GraphitiClient",
            targets: ["GraphitiClient"]),
        .executable(name: "Examples", targets: ["Examples"])
    ],
    dependencies: [
        .package(url: "https://github.com/apple/swift-http-types.git", from: "1.3.0"),
        .package(url: "https://github.com/swift-server/async-http-client.git", from: "1.23.0"),
    ],
    targets: [
        .target(
            name: "GraphitiClient",
            dependencies: [
                .product(name: "HTTPTypes", package: "swift-http-types"),
                .product(name: "HTTPTypesFoundation", package: "swift-http-types"),
                .product(name: "AsyncHTTPClient", package: "async-http-client"),
            ],
            path: "graphiti-swift/Sources/GraphitiClient",
            swiftSettings: [
                .enableExperimentalFeature("StrictConcurrency")
            ]
        ),
        .testTarget(
            name: "GraphitiClientTests",
            dependencies: ["GraphitiClient"],
            path: "graphiti-swift/Tests/GraphitiClientTests",
        ),
        .executableTarget(name: "Examples", dependencies: ["GraphitiClient"], path: "graphiti-swift/Examples")
    ]
)
