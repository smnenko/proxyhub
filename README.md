# ProxyHub
Python package to parse and check proxies from github repositories.

### Installation
```
pip install git+https://github.com/smnenko/proxyhub.git
```

### Example

```python
from proxyhub import ProxyHub


if __name__ == '__main__':
    sources = [
        # Find some proxy list sources on github
        # and put there urls to raw pages with proxies
        # For example: 
        # https://raw.githubusercontent.com/<user>/<repo>/<branch>/<file>
    ]
    
    ph = ProxyHub(sources=sources)
    
    print(ph.get())
    print(ph.get())
    print(ph.get())
    print(ph.get())
```

### License
ProxyHub is packaged and distributed using the MIT License which allows for commercial use, distribution, modification and private use provided that all copies of the software contain the same license and copyright.

By the community, for the community.
A passion project by Stanislav Semenenko