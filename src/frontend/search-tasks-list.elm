module Main exposing (..)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Decode as JD
import Json.Decode.Pipeline as PL
import Debug exposing (log)


main =
    Html.program
        { init = init
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



-- MODEL


type alias SearchTask =
    { expanded : Bool
    , id : String
    , queryString : String
    , recurrence : String
    , server : String
    , product : Maybe String
    , nListings : Int
    , priceMin : Float
    , priceMax : Float
    , currency : String
    }


type alias Model =
    { tasks : List SearchTask
    , error : String
    }


init : ( Model, Cmd Msg )
init =
    ( Model [] ""
    , getTaskList
    )



-- UPDATE


type Msg
    = ReloadTasks
    | NewTasks (Result Http.Error (List SearchTask))


update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        ReloadTasks ->
            ( { model | tasks = [] }, getTaskList )

        NewTasks (Ok newTasks) ->
            ( { model | tasks = List.append model.tasks newTasks }, Cmd.none )

        NewTasks (Err err) ->
            ( { model | error = (toString err) }, Cmd.none )



-- VIEW


view : Model -> Html Msg
view model =
    div []
        [ h2 [] [ text "Search Tasks" ]
        , br [] []
        , table []
            [ thead []
                [ tr []
                    [ th [] [ text "ID" ]
                    , th [] [ text "Product" ]
                    , th [] [ text "Query String" ]
                    , th [] [ text "Server" ]
                    , th [] [ text "Recurrence" ]
                    , th [] [ text "Number Listings" ]
                    , th [] [ text "Price Min" ]
                    , th [] [ text "Price Max" ]
                    , th [] [ text "Currency" ]
                    ]
                ]
            , tbody []
                (List.map viewSearchTask model.tasks)
            ]
        , viewError model
        ]


viewSearchTask : SearchTask -> Html Msg
viewSearchTask task =
    tr []
        [ td [] [ text task.id ]
        , td [] [ text "-" ] --"product": null,
        , td [] [ text task.queryString ]
        , td [] [ text task.server ]
        , td [] [ text task.recurrence ]
        , td [] [ text (toString task.nListings) ]
        , td [] [ text (toString task.priceMin) ]
        , td [] [ text (toString task.priceMax) ]
        , td [] [ text task.currency ]
        ]


viewError : Model -> Html Msg
viewError model =
    if model.error == "" then
        div [] []
    else
        div
            [ style
                [ ( "color", "red" )
                , ( "font-weight", "bold" )
                ]
            ]
            [ text ("Error: " ++ model.error) ]



-- SUBSCRIPTIONS


subscriptions : Model -> Sub Msg
subscriptions model =
    Sub.none



-- HTTP


{-| The API URL for accessing search tasks.
-}
url_SEARCH_TASKS : String
url_SEARCH_TASKS =
    --"/collect/api/search_tasks/"
    "http://localhost:8000/collect/api/search_tasks/"


getTaskList : Cmd Msg
getTaskList =
    Http.send NewTasks (Http.get url_SEARCH_TASKS parseSearchTaskList)


{-| Parse the JSON response from the "Search Tasks" API.

The JSON has the following form:

    """
    {
        "count": 2,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 1,
                "recurrence": "3 00:00:00",
                "server": "EBAY-DE",
                "product": null,
                "query_string": "Nikon D90",
                "n_listings": 50,
                "price_min": 100.0,
                "price_max": 500.0,
                "currency": "EUR"
            },
            {...}
        ]
    }
    """

-}
parseSearchTaskList : JD.Decoder (List SearchTask)
parseSearchTaskList =
    JD.at [ "results" ]
        (JD.list
            (PL.decode SearchTask
                |> PL.hardcoded False
                |> PL.required "id" (JD.map toString JD.int)
                |> PL.required "query_string" JD.string
                |> PL.required "recurrence" JD.string
                |> PL.required "server" JD.string
                |> PL.required "product" (JD.nullable JD.string)
                |> PL.required "n_listings" JD.int
                |> PL.required "price_min" JD.float
                |> PL.required "price_max" JD.float
                |> PL.required "currency" JD.string
            )
        )
