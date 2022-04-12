#include <string_view>

#include <HelloWorld/translation.h>

const auto stringOne = _TR("This is a line of text which will be translated"); // NOLINT don't care about anything it's just an example
const auto stringTwo = _TR("Another line of text"); // NOLINT
const auto stringTwo2 = _TR("Another line of text", "With disambiguation"); // NOLINT
const auto stringThree = _TR("One more line", "With more details"); // NOLINT

namespace ns1
{
    const auto stringThree = _TR("This one is declared within a namespace"); // NOLINT
}


int main()
{
    // These aren't the use-case, but included anyway to test if we can handle them.
    printMessage(stringOne);
    printMessage(stringTwo);
    printMessage(stringTwo2);
    printMessage(stringThree);
    printMessage(ns1::stringThree);

    printMessage(_TR("This is the way we meant to be used"));
    printMessage(_TR("This is the way we meant to be used")); // This should be grouped with the other identical string
    printMessage(_TR("This is the way we meant to be used", "This is a disambiguation")); // This not, because we meant something else

    printMessage(_TR("This is a {feature} which uses some {param}."), { { "feature", "template" }, { "param", "placeholder texts" } });

    for (size_t i = 1; i < 5; ++i) // NOLINT
    {
        printMessage(i <= 1 ? _TR("We have {how_many} thing") : _TR("We have {how_many} things"), { { "how_many", std::to_string(i) } });
    }

    // TODO: Add more scenarios - but it's most likely not necessarily needed
}
