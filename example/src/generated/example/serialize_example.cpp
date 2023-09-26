/*
 * WARNING: This is an automatically generated source file.
 * Do NOT modify it manually.
*/

#include <nlohmann/json.hpp>

#include "D:/prog/SerializerPOC/example/src/../include/example/example.hpp"

using json = nlohmann::json;

namespace ns1::ns2
{
	void from_json(const json & j, A & o)
	{
		j.at("a").get_to(o.a);
		j.at("b").get_to(o.b);
	}

	void to_json(json & j, const A & o)
	{
		j["a"] = o.a;
		j["b"] = o.b;
	}
} // namespace ns1::ns2

namespace ns1::ns2
{
	void from_json(const json & j, B & o)
	{
		j.at("a").get_to(o.a);
		j.at("b").get_to(o.b);
	}

	void to_json(json & j, const B & o)
	{
		j["a"] = o.a;
		j["b"] = o.b;
	}
} // namespace ns1::ns2
