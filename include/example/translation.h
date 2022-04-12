//
// Created by psari on 23. 7. 2020.
//

#ifndef CODEGENERATIONPOC_TRANSLATION_H
#define CODEGENERATIONPOC_TRANSLATION_H

#include <string_view>
#include <string>
#include <map>
#include <cstddef>
#include <iostream>

struct TranslationRecord
{
    std::string_view message;
    std::string_view disambiguation;
    std::string_view file;
};


#define TRANSLATION_STRING_1_ARGS(message) TranslationRecord({ message, "", __FILE__ })
#define TRANSLATION_STRING_2_ARGS(message, distinguishment) TranslationRecord({ message, distinguishment, __FILE__ })

#define TRANSLATION_MACRO_GET_3RD_ARG(arg1, arg2, arg3, ...) arg3
#define TRANSLATION_MACRO_SELECTOR(...) TRANSLATION_MACRO_GET_3RD_ARG(__VA_ARGS__, TRANSLATION_STRING_2_ARGS, TRANSLATION_STRING_1_ARGS)

#define _TR(...) TRANSLATION_MACRO_SELECTOR(__VA_ARGS__)(__VA_ARGS__)

// ---
// Example printer

void printMessage(const TranslationRecord & record)
{
    // <this is where you would look up the translation of the string using the record>
    std::cout << record.file << ' ' << record.message << " (" << record.disambiguation << ')' << '\n';
}

void stringReplace(std::string & str, const std::string & from, const std::string & to)
{
    if (from.empty()) return;
    size_t start_pos = 0;
    while ((start_pos = str.find(from, start_pos)) != std::string::npos) {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx'
    }
}

void printMessage(const TranslationRecord && record, const std::map<std::string, std::string> && params)
{
    // <this is where you would look up the translation of the string using the record>
    std::string message = record.message.data();
    // Look a bit more like fmt compatible - in bigger scale, we definitely should use it.
    for (const auto & param : params) { stringReplace(message, "{" + param.first + "}", param.second); }
    std::cout << record.file << ' ' << message << " (" << record.disambiguation << ')' << '\n';
}

#endif // CODEGENERATIONPOC_TRANSLATION_H
