# TypeScript Basics Comprehensive Guide

## What is TypeScript?
TypeScript is a statically typed superset of JavaScript that compiles to plain JavaScript, providing type safety and modern language features.

## Installation:
```bash
npm install -g typescript
# or for project-specific
npm install --save-dev typescript
```

## Basic Types:
```typescript
// Primitive types
let isDone: boolean = false;
let decimal: number = 6;
let color: string = "blue";
let list: number[] = [1, 2, 3];
let tuple: [string, number] = ["hello", 10];

// Any type (avoid when possible)
let notSure: any = 4;

// Void type
function warnUser(): void {
    console.log("This is a warning message");
}

// Null and Undefined
let u: undefined = undefined;
let n: null = null;
```

## Interfaces:
```typescript
interface User {
    id: number;
    name: string;
    email?: string; // Optional property
    readonly created: Date; // Readonly property
}

function getUser(id: number): User {
    return {
        id,
        name: "John Doe",
        created: new Date()
    };
}
```

## Function Types:
```typescript
// Function type annotation
function add(x: number, y: number): number {
    return x + y;
}

// Arrow function
const multiply = (x: number, y: number): number => x * y;

// Optional parameters
function buildName(firstName: string, lastName?: string): string {
    return lastName ? `${firstName} ${lastName}` : firstName;
}

// Default parameters
function greet(name: string = "World"): string {
    return `Hello, ${name}!`;
}
```

## Union and Intersection Types:
```typescript
// Union types
type StringOrNumber = string | number;
let value: StringOrNumber = "hello";
value = 42; // Also valid

// Intersection types
interface ErrorHandling {
    success: boolean;
    error?: { message: string };
}

interface ArtworksData {
    artworks: { title: string }[];
}

type ArtworksResponse = ArtworksData & ErrorHandling;
```

## Generics:
```typescript
// Generic function
function identity<T>(arg: T): T {
    return arg;
}

// Generic interface
interface GenericIdentityFn<T> {
    (arg: T): T;
}

// Generic class
class GenericNumber<T> {
    zeroValue: T;
    add: (x: T, y: T) => T;
}
```

## Classes:
```typescript
class Animal {
    private name: string;
    protected species: string;
    public age: number;

    constructor(name: string, species: string, age: number) {
        this.name = name;
        this.species = species;
        this.age = age;
    }

    public getName(): string {
        return this.name;
    }
}

class Dog extends Animal {
    constructor(name: string, age: number) {
        super(name, "Canine", age);
    }

    public bark(): void {
        console.log("Woof!");
    }
}
```

## Type Assertions:
```typescript
// Type assertion
let someValue: any = "this is a string";
let strLength: number = (someValue as string).length;

// Alternative syntax
let strLength2: number = (<string>someValue).length;
```