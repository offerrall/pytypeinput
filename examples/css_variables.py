from pytypeinput.html import HTMLRenderer


def main():
    print("=" * 60)
    print("Available CSS Variables")
    print("=" * 60)
    
    variables = HTMLRenderer.list_css_variables()
    
    print(f"\nFound {len(variables)} CSS variables:\n")
    
    for var in variables:
        print(f"  {var}")


if __name__ == "__main__":
    main()